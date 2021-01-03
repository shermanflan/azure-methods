from collections import defaultdict
from datetime import datetime
import json
import logging

import ijson
import pandas as pd
import pyarrow as pa
from pyarrow.parquet import ParquetWriter
import requests
from requests.exceptions import HTTPError

from devops_api import (
    LAKE_CONTAINER, LAKE_PATH,
    BLOB_ACCOUNT, BLOB_ACCOUNT_KEY,
    BLOB_CONTAINER, BLOB_PATH,
    SQL_DRIVER, SQL_HOST, SQL_DB,
    SQL_USER, SQL_PWD
)
from devops_api.api.aha import get_account_backup
from devops_api.api.blob import AzureBlobHook
from devops_api.api.lake import LakeFactory
from devops_api.db.mssql import SqlWriter
from devops_api.utils import log
from devops_api.utils.error import RetryableError

logger = logging.getLogger(__name__)

PROJECT_PQ = pa.schema([
    pa.field('aha_id', pa.string()),
    pa.field('reference_prefix', pa.string()),
    pa.field('name', pa.string()),
    pa.field('last_release_num', pa.int32()),
    pa.field('last_feature_num', pa.int32()),
    pa.field('last_idea_num', pa.int32()),
    pa.field('position', pa.int32()),
    pa.field('positioning_customer', pa.string()),
    pa.field('positioning_problem', pa.string()),
    pa.field('positioning_benefit1', pa.string()),
    pa.field('positioning_benefit2', pa.string()),
    pa.field('positioning_benefit3', pa.string()),
    pa.field('product_line', pa.bool_()),
    pa.field('product_line_type', pa.string()),
    pa.field('capacity_planning_enabled', pa.bool_()),
    pa.field('ideas_scoring_system_id', pa.string()),
    pa.field('ideas_default_user_id', pa.string()),
    pa.field('default_capacity_units', pa.int32()),
    pa.field('default_feature_remaining_estimate', pa.bool_()),
    pa.field('last_page_num', pa.int32()),
    pa.field('color', pa.int32()),
    pa.field('workflow_screen_enabled', pa.bool_()),
    pa.field('competitor_scoring_system_id', pa.string()),
    pa.field('initiative_workflow_id', pa.string()),
    pa.field('strategic_imperative_workflow_id', pa.string()),
    pa.field('estimated_time_as_work_done', pa.bool_()),
    pa.field('last_epic_num', pa.int32()),
    pa.field('configuration', pa.string()),
    pa.field('workspace_type', pa.string()),
    pa.field('created_at', pa.timestamp('ms')),
    pa.field('updated_at', pa.timestamp('ms')),
    pa.field('parent_id', pa.string()),
    pa.field('scoring_system_id', pa.string()),
    pa.field('idea_workflow_id', pa.string()),
    pa.field('feature_workflow_id', pa.string()),
    pa.field('release_workflow_id', pa.string()),
])

IDEA_PQ = pa.schema([
    pa.field('aha_id', pa.string()),
    pa.field('reference_num', pa.string()),
    pa.field('name', pa.string()),
    pa.field('score', pa.int32()),
    pa.field('visibility', pa.int32()),
    pa.field('num_endorsements', pa.int32()),
    pa.field('initial_votes', pa.int32()),
    pa.field('contributorship_type', pa.string()),
    pa.field('promotable_type', pa.string()),
    pa.field('is_spam', pa.bool_()),
    pa.field('created_at', pa.timestamp('ms')),
    pa.field('updated_at', pa.timestamp('ms')),
    pa.field('project_id', pa.string()),
    pa.field('promotable_id', pa.string()),
    pa.field('contributorship_id', pa.string()),
    pa.field('workflow_status_id', pa.string()),
])

REQUIREMENT_PQ = pa.schema([
    pa.field('aha_id', pa.string()),
    pa.field('reference_num', pa.string()),
    pa.field('created_by_user_id', pa.string()),
    pa.field('position', pa.int32()),
    pa.field('original_estimate', pa.float32()),
    pa.field('remaining_estimate', pa.float32()),
    pa.field('work_done', pa.float32()),
    pa.field('name', pa.string()),
    pa.field('created_at', pa.timestamp('ms')),
    pa.field('updated_at', pa.timestamp('ms')),
    pa.field('feature_id', pa.string()),
    pa.field('project_id', pa.string()),
    pa.field('workflow_status_id', pa.string()),
    pa.field('assigned_to_user_id', pa.string()),
])


if __name__ == '__main__':

    # TODO: Request backup
    # TODO: Handle HTTP 429 if a backup was already created within the last 24 hours
    # TODO: Poller every 5 min
    # tmp_dir = '/home/condesa1931/personal/github/azure-methods/DevOpsAPI/data'
    # backup_path = get_account_backup(backup_id="6911382328887923514",
    #                                  out_directory=tmp_dir)
    backup_path = f"./data/aha-account-6240998105453674102-backup-2020-12-28-18-53.json"
    project_path = f"./data/aha-project-backup-2020-12-28-18-53.parquet"
    idea_path = f"./data/aha-idea-backup-2020-12-28-18-53.parquet"
    requirement_path = f"./data/aha-requirement-backup-2020-12-28-18-53.parquet"

    with open(backup_path, 'rt', encoding='utf-8') as f, \
            ParquetWriter(project_path, PROJECT_PQ, compression='SNAPPY') as p, \
            ParquetWriter(idea_path, IDEA_PQ, compression='SNAPPY') as i, \
            ParquetWriter(requirement_path, REQUIREMENT_PQ, compression='SNAPPY') as r:

        class_types = [
            'Account',
            'AccountUser',
            'AccountWorkflow',
            'Annotation::Point',
            'Approval',
            'BusinessModel',
            'BusinessModelComponent',
            'Comment',
            'Competitor',
            'CustomFieldDefinitions::DateField',
            'CustomFieldDefinitions::LinkMasterDetail',
            'CustomFieldDefinitions::NoteField',
            'CustomFieldDefinitions::NumberField',
            'CustomFieldDefinitions::Records::InitiativesField',
            'CustomFieldDefinitions::Records::ProjectsField',
            'CustomFieldDefinitions::Records::StrategicImperativesField',
            'CustomFieldDefinitions::Records::UsersField',
            'CustomFieldDefinitions::ScorecardField',
            'CustomFieldDefinitions::SelectConstant',
            'CustomFieldDefinitions::SelectEditable',
            'CustomFieldDefinitions::SelectMultipleEditable',
            'CustomFieldDefinitions::TextField',
            'CustomFieldDefinitions::UrlField',
            'CustomFieldOption',
            'CustomFieldValues::DateField',
            'CustomFieldValues::NoteField',
            'CustomFieldValues::NumberField',
            'CustomFieldValues::RecordsField',
            'CustomFieldValues::ScorecardField',
            'CustomFieldValues::SelectConstant',
            'CustomFieldValues::SelectEditable',
            'CustomFieldValues::SelectMultipleEditable',
            'CustomFieldValues::TextField',
            'CustomFieldValues::UrlField',
            'CustomObjectDefinition',
            'CustomObjectRecord',
            'Epic',
            'Epoch',
            'Feature',
            'Ideas::Idea',
            'Ideas::IdeaComment',
            'Ideas::IdeaEndorsement',
            'Ideas::IdeaPortal',
            'Ideas::IdeaPortalDomain',
            'Ideas::IdeaPortalProject',
            'Ideas::IdeaResponse',
            'Ideas::PortalUser',
            'Initiative',
            'InitiativeImpact',
            'Integration::IntegrationV1',
            'Integration::IntegrationV2',
            'IntegrationField',
            'MasterRelease',
            'Note',
            'Page',
            'PaidSeatGroup::Administration',
            'PaidSeatGroup',
            'Persona',
            'Project',
            'ProjectNavigation',
            'ProjectScreen',
            'ProjectStrategy',
            'ProjectStrategyComponent',
            'ProjectUser',
            'RecordLink',
            'Release',
            'ReleasePhase',
            'Requirement',
            'ScoreFact',
            'ScoringSystem',
            'ScoringSystemMetric',
            'ScreenDefinition',
            'ScreenDefinitionControl',
            'StrategicImpact',
            'StrategicImperative',
            'StrategicImperativeBackground',
            'StrategicImperativeMetric',
            'Tag',
            'Tagging',
            'Task',
            'TaskUser',
            'User',
            'Workflow',
            'WorkflowKind',
            'WorkflowStatus',
            'WorkflowStatusTime',
        ]
        classes = defaultdict(int)

        logger.info(f"Shredding JSON input")
        objects = ijson.items(f, 'records.item')
        project, idea, requirement = [], [], []

        for record in objects:
            classes[record['class']] += 1

            if record['class'] == 'Project':
                project.append((
                    record['id'],
                    record['fields']['reference_prefix'],
                    record['fields']['name'],
                    record['fields']['last_release_num'],
                    record['fields']['last_feature_num'],
                    record['fields']['last_idea_num'],
                    record['fields']['position'],
                    record['fields']['positioning_customer'],
                    record['fields']['positioning_problem'],
                    record['fields']['positioning_benefit1'],
                    record['fields']['positioning_benefit2'],
                    record['fields']['positioning_benefit3'],
                    record['fields']['product_line'],
                    record['fields']['product_line_type'],
                    record['fields']['capacity_planning_enabled'],
                    str(record['fields'].get('ideas_scoring_system_id')),
                    record['fields']['ideas_default_user_id'],
                    record['fields']['default_capacity_units'],
                    record['fields']['default_feature_remaining_estimate'],
                    record['fields']['last_page_num'],
                    record['fields']['color'],
                    record['fields']['workflow_screen_enabled'],
                    str(record['fields']['competitor_scoring_system_id']),
                    str(record['fields']['initiative_workflow_id']),
                    str(record['fields']['strategic_imperative_workflow_id']),
                    record['fields']['estimated_time_as_work_done'],
                    record['fields']['last_epic_num'],
                    json.dumps(record['fields']['configuration']),
                    record['fields']['workspace_type'],
                    datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    record['links'].get('parent_id'),
                    record['links'].get('scoring_system_id'),
                    record['links']['idea_workflow_id'],
                    record['links']['feature_workflow_id'],
                    record['links']['release_workflow_id'],
                ))
                if len(project) % 10 == 0:
                    tmp_df = pd.DataFrame(project, columns=[x.name for x in PROJECT_PQ])
                    p.write_table(pa.Table.from_pandas(tmp_df, schema=PROJECT_PQ))
                    project = []
            elif record['class'] == 'Ideas::Idea':
                idea.append((
                    record['id'],
                    record['fields']['reference_num'],
                    record['fields']['name'][:512],
                    record['fields']['score'],
                    record['fields']['visibility'],
                    record['fields']['num_endorsements'],
                    record['fields']['initial_votes'],
                    record['fields']['contributorship_type'],
                    record['fields']['promotable_type'],
                    record['fields']['is_spam'],
                    datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    record['links']['project_id'],
                    record['links'].get('promotable_id'),
                    record['links']['contributorship_id'],
                    record['links']['workflow_status_id'],
                ))
                if len(idea) % 100 == 0:
                    tmp_df = pd.DataFrame(idea, columns=[x.name for x in IDEA_PQ])
                    i.write_table(pa.Table.from_pandas(tmp_df, schema=IDEA_PQ))
                    idea = []
            # elif record['class'] == 'User':
            #     db.write_record(USER, (
            #         record['id'],
            #         record['fields']['first_name'],
            #         record['fields']['last_name'],
            #         record['fields']['email'],
            #         record['fields']['timezone'],
            #         record['fields']['locale'],
            #         record['fields']['unsubscribe_lifecycle_emails'],
            #         record['fields']['unsubscribe_all_notifications'],
            #         record['fields']['email_verified'],
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #     ))
            # elif record['class'] == 'Release':
            #     db.write_record(RELEASE, (
            #         record['id'],
            #         record['fields']['reference_num'],
            #         record['fields']['name'],
            #         datetime.strptime(record['fields']['release_date'], "%Y-%m-%d"),
            #         datetime.strptime(record['fields']['released_on'], "%Y-%m-%d")
            #             if record['fields']['released_on'] else None,
            #         record['fields']['progress'],
            #         record['fields']['progress_source'],
            #         datetime.strptime(record['fields']['development_started_on'], "%Y-%m-%d")
            #             if record['fields']['development_started_on'] else None,
            #         datetime.strptime(record['fields']['external_release_date'], "%Y-%m-%d"),
            #         record['fields']['external_date_resolution'],
            #         record['fields']['total_capacity'],
            #         record['fields']['capacity_units'],
            #         record['fields']['parking_lot'],
            #         record['fields']['type'],
            #         datetime.strptime(record['fields']['start_on'], "%Y-%m-%d")
            #             if record['fields']['start_on'] else None,
            #         record['fields']['created_by_user_id'],
            #         record['fields']['duration_source'],
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         record['links']['project_id'],
            #         record['links']['workflow_status_id'],
            #         record['links']['owner_id'],
            #     ))
            # elif record['class'] == 'Feature':
            #     db.write_record(FEATURE, (
            #         record['id'],
            #         record['fields']['reference_num'],
            #         record['fields']['position'],
            #         record['fields']['name'],
            #         record['fields']['score'],
            #         record['fields']['last_requirement_num'],
            #         record['fields']['progress'],
            #         record['fields']['progress_source'],
            #         record['fields']['show_feature_remaining_estimate'],
            #         datetime.strptime(record['fields']['due_date'], "%Y-%m-%d")
            #             if record['fields']['due_date'] else None,
            #         datetime.strptime(record['fields']['start_date'], "%Y-%m-%d")
            #             if record['fields']['start_date'] else None,
            #         record['fields']['duration_estimate'],
            #         record['fields']['original_estimate'],
            #         record['fields']['remaining_estimate'],
            #         record['fields']['work_done'],
            #         datetime.strptime(record['fields']['status_changed_on'], "%Y-%m-%d")
            #             if record['fields']['status_changed_on'] else None,
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         record['links'].get('epic_id'),
            #         record['links']['project_id'],
            #         record['links']['release_id'],
            #         record['links'].get('initiative_id'),
            #         record['links'].get('assigned_to_user_id'),
            #         record['links']['created_by_user_id'],
            #         record['links']['workflow_status_id'],
            #         record['links']['workflow_kind_id'],
            #     ))
            elif record['class'] == 'Requirement':
                requirement.append((
                    record['id'],
                    record['fields']['reference_num'],
                    str(record['fields']['created_by_user_id']),
                    record['fields']['position'],
                    float(record['fields']['original_estimate'])
                        if record['fields']['original_estimate'] else None,
                    float(record['fields']['remaining_estimate'])
                        if record['fields']['remaining_estimate'] else None,
                    float(record['fields']['work_done'])
                        if record['fields']['work_done'] else None,
                    record['fields']['name'],
                    datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    record['links']['feature_id'],
                    record['links']['project_id'],
                    record['links']['workflow_status_id'],
                    record['links'].get('assigned_to_user_id'),
                ))
                if len(requirement) % 1000 == 0:
                    tmp_df = pd.DataFrame(requirement, columns=[x.name for x in REQUIREMENT_PQ])
                    r.write_table(pa.Table.from_pandas(tmp_df, schema=REQUIREMENT_PQ))
                    requirement = []
            # elif record['class'] == 'IntegrationField':
            #     db.write_record(INTEGRATION, (
            #         record['id'],
            #         record['fields']['name'],
            #         record['fields']['value'],
            #         record['fields']['integratable_type'],
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         record['links']['account_id'],
            #         record['links']['integration_id'],
            #         record['links']['integratable_id'],
            #     ))
            # elif record['class'] == 'Epic':
            #     db.write_record(EPIC, (
            #         record['id'],
            #         record['fields']['reference_num'],
            #         record['fields']['position'],
            #         record['fields']['name'],
            #         record['fields']['score'],
            #         record['fields']['progress'],
            #         record['fields']['progress_source'],
            #         record['fields']['show_feature_remaining_estimate'],
            #         datetime.strptime(record['fields']['due_date'], "%Y-%m-%d")
            #             if record['fields']['due_date'] else None,
            #         datetime.strptime(record['fields']['start_date'], "%Y-%m-%d")
            #             if record['fields']['start_date'] else None,
            #         record['fields']['duration_estimate'],
            #         record['fields']['original_estimate'],
            #         record['fields']['remaining_estimate'],
            #         record['fields']['work_done'],
            #         datetime.strptime(record['fields']['status_changed_on'], "%Y-%m-%d")
            #             if record['fields']['status_changed_on'] else None,
            #         record['fields']['duration_source'],
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         record['links']['release_id'],
            #         record['links']['project_id'],
            #         record['links'].get('initiative_id'),
            #         record['links']['created_by_user_id'],
            #         record['links']['workflow_status_id'],
            #     ))
            # elif record['class'] == 'Initiative':
            #     db.write_record(INITIATIVE, (
            #         record['id'],
            #         record['fields']['reference_num'],
            #         record['fields']['name'],
            #         record['fields']['color'],
            #         record['fields']['position'],
            #         record['fields']['value'],
            #         record['fields']['effort'],
            #         record['fields']['presented'],
            #         datetime.strptime(record['fields']['start_date'], "%Y-%m-%d")
            #             if record['fields']['start_date'] else None,
            #         datetime.strptime(record['fields']['end_date'], "%Y-%m-%d")
            #             if record['fields']['end_date'] else None,
            #         record['fields']['progress'],
            #         record['fields']['progress_source'],
            #         record['fields']['duration_source'],
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         record['links']['project_id'],
            #         record['links'].get('epoch_id'),
            #         record['links']['workflow_status_id'],
            #     ))
            # elif record['class'] == 'Epoch':
            #     db.write_record(EPOCH, (
            #         record['id'],
            #         record['fields']['name'],
            #         record['fields']['archived'],
            #         datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            #         record['links']['account_id'],
            #     ))

        if project:
            tmp_df = pd.DataFrame(project, columns=[x.name for x in PROJECT_PQ])
            p.write_table(pa.Table.from_pandas(tmp_df, schema=PROJECT_PQ))
        if idea:
            tmp_df = pd.DataFrame(idea, columns=[x.name for x in IDEA_PQ])
            i.write_table(pa.Table.from_pandas(tmp_df, schema=IDEA_PQ))
        if requirement:
            tmp_df = pd.DataFrame(requirement, columns=[x.name for x in REQUIREMENT_PQ])
            r.write_table(pa.Table.from_pandas(tmp_df, schema=REQUIREMENT_PQ))

    logger.info(f"Writing to data lake")

    files = [
        f"./data/aha-project-backup-2020-12-28-18-53.parquet",
        f"./data/aha-idea-backup-2020-12-28-18-53.parquet",
        f"./data/aha-requirement-backup-2020-12-28-18-53.parquet"
    ]
    # blob_hook = AzureBlobHook(account_name=BLOB_ACCOUNT,
    #                          account_key=BLOB_ACCOUNT_KEY)
    # blob_hook.upload_files(container_name=BLOB_CONTAINER,
    #                        blob_dir=BLOB_PATH, files=files)
    LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                               lake_dir=LAKE_PATH, files=files)

    sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
    # logger.info(f"{json.dumps(sorted_classes, indent=4)}")
    logger.info(f"Found {len(sorted_classes)} classes")

    logger.info("Process complete")
