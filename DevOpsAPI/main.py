from collections import defaultdict
from datetime import datetime
import json
import logging

import ijson
import requests
from requests.exceptions import HTTPError

from devops_api import (
    AHA_ENDPOINT, AHA_APP_KEY,
    AHA_USER, AHA_PWD,
    SQL_DRIVER, SQL_HOST, SQL_DB,
    SQL_USER, SQL_PWD
)
from devops_api.io.mssql import SqlWriter
from devops_api.utils import log
from devops_api.utils.error import RetryableError

logger = logging.getLogger(__name__)


def get_account_backup(backup_id):
    """

    :param backup_id:
    :type backup_id: String
    :return: path to account_backup as String
    """
    with requests.Session() as session:
        try:
            resource = "account_backups"
            backup_uri = f"{AHA_ENDPOINT}/{resource}/{backup_id}.tgz"
            headers = {
                "Authorization": f"Bearer {AHA_APP_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            r = session.get(backup_uri, headers=headers, stream=True)
            r.raise_for_status()

            save_path = f"./data/{backup_id}.tgz"

            with open(save_path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=512):
                    fd.write(chunk)

            # TODO: unzip => tar -xf 6911382328887923514.tgz
            return save_path
        except HTTPError as e:

            # logger.error(f'Request error', status_code=r.status_code, source=backup_uri)
            logger.exception(e)

            if e.response.status_code in (429, 503, 504):
                logger.error('Server overloaded')
                raise RetryableError('Retrying account backup download')

            raise


project_dml = """
INSERT INTO [Staging].[AhaProject] 
(
    [aha_id]
    ,[reference_prefix]
    ,[name]
    ,[last_release_num]
    ,[last_feature_num]
    ,[last_idea_num]
    ,[position]
    ,[positioning_customer]
    ,[positioning_problem]
    ,[positioning_benefit1]
    ,[positioning_benefit2]
    ,[positioning_benefit3]
    ,[product_line]
    ,[product_line_type]
    ,[capacity_planning_enabled]
    ,[ideas_scoring_system_id]
    ,[ideas_default_user_id]
    ,[default_capacity_units]
    ,[default_feature_remaining_estimate]
    ,[last_page_num]
    ,[color]
    ,[workflow_screen_enabled]
    ,[competitor_scoring_system_id]
    ,[initiative_workflow_id]
    ,[strategic_imperative_workflow_id]
    ,[estimated_time_as_work_done]
    ,[last_epic_num]
    ,[configuration]
    ,[workspace_type]
    ,[created_at]
    ,[updated_at]
    ,[parent_id]
    ,[scoring_system_id]
    ,[idea_workflow_id]
    ,[feature_workflow_id]
    ,[release_workflow_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

idea_dml = """
INSERT INTO [Staging].[AhaIdea] 
(
    [aha_id]
    ,[reference_num]
    ,[name]
    ,[score]
    ,[visibility]
    ,[num_endorsements]
    ,[initial_votes]
    ,[contributorship_type]
    ,[promotable_type]
    ,[is_spam]
    ,[created_at]
    ,[updated_at]
    ,[project_id]
    ,[promotable_id]
    ,[contributorship_id]
    ,[workflow_status_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

user_dml = """
INSERT INTO [Staging].[AhaUser]
(
    [aha_id]
    ,[first_name]
    ,[last_name]
    ,[email]
    ,[timezone]
    ,[locale]
    ,[unsubscribe_lifecycle_emails]
    ,[unsubscribe_all_notifications]
    ,[email_verified]
    ,[created_at]
    ,[updated_at]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

release_dml = """
INSERT INTO [Staging].[AhaRelease]
(
    [aha_id]
    ,[reference_num]
    ,[name]
    ,[release_date]
    ,[released_on]
    ,[progress]
    ,[progress_source]
    ,[development_started_on]
    ,[external_release_date]
    ,[external_date_resolution]
    ,[total_capacity]
    ,[capacity_units]
    ,[parking_lot]
    ,[type]
    ,[start_on]
    ,[created_by_user_id]
    ,[duration_source]
    ,[created_at]
    ,[updated_at]
    ,[project_id]
    ,[workflow_status_id]
    ,[owner_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

feature_dml = """
INSERT INTO [Staging].[AhaFeature]
(
    [aha_id]
    ,[reference_num]
    ,[position]
    ,[name]
    ,[score]
    ,[last_requirement_num]
    ,[progress]
    ,[progress_source]
    ,[show_feature_remaining_estimate]
    ,[due_date]
    ,[start_date]
    ,[duration_estimate]
    ,[original_estimate]
    ,[remaining_estimate]
    ,[work_done]
    ,[status_changed_on]
    ,[created_at]
    ,[updated_at]
    ,[epic_id]
    ,[project_id]
    ,[release_id]
    ,[initiative_id]
    ,[assigned_to_user_id]
    ,[created_by_user_id]
    ,[workflow_status_id]
    ,[workflow_kind_id]
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

requirement_dml = """
INSERT INTO [Staging].[AhaRequirement]
(
    [aha_id]
    ,[reference_num]
    ,[created_by_user_id]
    ,[position]
    ,[original_estimate]
    ,[remaining_estimate]
    ,[work_done]
    ,[name]
    ,[created_at]
    ,[updated_at]
    ,[feature_id]
    ,[project_id]
    ,[workflow_status_id]
    ,[assigned_to_user_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

integration_field_dml = """
INSERT INTO [Staging].[AhaIntegrationField]
(
    [aha_id]
    ,[name]
    ,[value]
    ,[integratable_type]
    ,[created_at]
    ,[updated_at]
    ,[account_id]
    ,[integration_id]
    ,[integratable_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

epic_dml = """
INSERT INTO [Staging].[AhaEpic]
(
    [aha_id]
    ,[reference_num]
    ,[position]
    ,[name]
    ,[score]
    ,[progress]
    ,[progress_source]
    ,[show_feature_remaining_estimate]
    ,[due_date]
    ,[start_date]
    ,[duration_estimate]
    ,[original_estimate]
    ,[remaining_estimate]
    ,[work_done]
    ,[status_changed_on]
    ,[duration_source]
    ,[created_at]
    ,[updated_at]
    ,[release_id]
    ,[project_id]
    ,[initiative_id]
    ,[created_by_user_id]
    ,[workflow_status_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

initiative_dml = """
INSERT INTO [Staging].[AhaInitiative]
(
    [aha_id]
    ,[reference_num]
    ,[name]
    ,[color]
    ,[position]
    ,[value]
    ,[effort]
    ,[presented]
    ,[start_date]
    ,[end_date]
    ,[progress]
    ,[progress_source]
    ,[duration_source]
    ,[created_at]
    ,[updated_at]
    ,[project_id]
    ,[epoch_id]
    ,[workflow_status_id]
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

epoch_dml = """
INSERT INTO [Staging].[AhaEpoch]
(
    [aha_id]
    ,[name]
    ,[archived]
    ,[created_at]
    ,[updated_at]
    ,[account_id]
)
VALUES (?, ?, ?, ?, ?, ?);
"""

if __name__ == '__main__':

    # TODO: Request backup
    # TODO: Handle HTTP 429 if a backup was already created within the last 24 hours
    # TODO: Poller every 5 min

    # backup_path = get_account_backup(backup_id="6911382328887923514")
    backup_path = f"./data/aha-account-6240998105453674102-backup-2020-12-28-18-53.json"

    with open(backup_path, 'rt', encoding='utf-8') as f:
        parser = ijson.parse(f)
        i = 0
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

        # Object-based
        objects = ijson.items(f, 'records.item')

        with SqlWriter(driver=SQL_DRIVER,
                       host=SQL_HOST,
                       db=SQL_DB,
                       uid=SQL_USER,
                       pwd=SQL_PWD) as db:

            for record in objects:
                classes[record['class']] += 1
                i += 1

                if record['class'] == 'Project':
                    db.write_record(project_dml, (
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
                        record['fields'].get('ideas_scoring_system_id'),
                        record['fields']['ideas_default_user_id'],
                        record['fields']['default_capacity_units'],
                        record['fields']['default_feature_remaining_estimate'],
                        record['fields']['last_page_num'],
                        record['fields']['color'],
                        record['fields']['workflow_screen_enabled'],
                        record['fields']['competitor_scoring_system_id'],
                        record['fields']['initiative_workflow_id'],
                        record['fields']['strategic_imperative_workflow_id'],
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
                elif record['class'] == 'Ideas::Idea':
                    db.write_record(idea_dml, (
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
                elif record['class'] == 'User':
                    db.write_record(user_dml, (
                        record['id'],
                        record['fields']['first_name'],
                        record['fields']['last_name'],
                        record['fields']['email'],
                        record['fields']['timezone'],
                        record['fields']['locale'],
                        record['fields']['unsubscribe_lifecycle_emails'],
                        record['fields']['unsubscribe_all_notifications'],
                        record['fields']['email_verified'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                    ))
                elif record['class'] == 'Release':
                    db.write_record(release_dml, (
                        record['id'],
                        record['fields']['reference_num'],
                        record['fields']['name'],
                        datetime.strptime(record['fields']['release_date'], "%Y-%m-%d"),
                        datetime.strptime(record['fields']['released_on'], "%Y-%m-%d")
                            if record['fields']['released_on'] else None,
                        record['fields']['progress'],
                        record['fields']['progress_source'],
                        datetime.strptime(record['fields']['development_started_on'], "%Y-%m-%d")
                            if record['fields']['development_started_on'] else None,
                        datetime.strptime(record['fields']['external_release_date'], "%Y-%m-%d"),
                        record['fields']['external_date_resolution'],
                        record['fields']['total_capacity'],
                        record['fields']['capacity_units'],
                        record['fields']['parking_lot'],
                        record['fields']['type'],
                        datetime.strptime(record['fields']['start_on'], "%Y-%m-%d")
                            if record['fields']['start_on'] else None,
                        record['fields']['created_by_user_id'],
                        record['fields']['duration_source'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links']['project_id'],
                        record['links']['workflow_status_id'],
                        record['links']['owner_id'],
                    ))
                elif record['class'] == 'Feature':
                    db.write_record(feature_dml, (
                        record['id'],
                        record['fields']['reference_num'],
                        record['fields']['position'],
                        record['fields']['name'],
                        record['fields']['score'],
                        record['fields']['last_requirement_num'],
                        record['fields']['progress'],
                        record['fields']['progress_source'],
                        record['fields']['show_feature_remaining_estimate'],
                        datetime.strptime(record['fields']['due_date'], "%Y-%m-%d")
                            if record['fields']['due_date'] else None,
                        datetime.strptime(record['fields']['start_date'], "%Y-%m-%d")
                            if record['fields']['start_date'] else None,
                        record['fields']['duration_estimate'],
                        record['fields']['original_estimate'],
                        record['fields']['remaining_estimate'],
                        record['fields']['work_done'],
                        datetime.strptime(record['fields']['status_changed_on'], "%Y-%m-%d")
                            if record['fields']['status_changed_on'] else None,
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links'].get('epic_id'),
                        record['links']['project_id'],
                        record['links']['release_id'],
                        record['links'].get('initiative_id'),
                        record['links'].get('assigned_to_user_id'),
                        record['links']['created_by_user_id'],
                        record['links']['workflow_status_id'],
                        record['links']['workflow_kind_id'],
                    ))
                elif record['class'] == 'Requirement':
                    db.write_record(requirement_dml, (
                        record['id'],
                        record['fields']['reference_num'],
                        record['fields']['created_by_user_id'],
                        record['fields']['position'],
                        record['fields']['original_estimate'],
                        record['fields']['remaining_estimate'],
                        record['fields']['work_done'],
                        record['fields']['name'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links']['feature_id'],
                        record['links']['project_id'],
                        record['links']['workflow_status_id'],
                        record['links'].get('assigned_to_user_id'),
                    ))
                elif record['class'] == 'IntegrationField':
                    db.write_record(integration_field_dml, (
                        record['id'],
                        record['fields']['name'],
                        record['fields']['value'],
                        record['fields']['integratable_type'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links']['account_id'],
                        record['links']['integration_id'],
                        record['links']['integratable_id'],
                    ))
                elif record['class'] == 'Epic':
                    db.write_record(epic_dml, (
                        record['id'],
                        record['fields']['reference_num'],
                        record['fields']['position'],
                        record['fields']['name'],
                        record['fields']['score'],
                        record['fields']['progress'],
                        record['fields']['progress_source'],
                        record['fields']['show_feature_remaining_estimate'],
                        datetime.strptime(record['fields']['due_date'], "%Y-%m-%d")
                            if record['fields']['due_date'] else None,
                        datetime.strptime(record['fields']['start_date'], "%Y-%m-%d")
                            if record['fields']['start_date'] else None,
                        record['fields']['duration_estimate'],
                        record['fields']['original_estimate'],
                        record['fields']['remaining_estimate'],
                        record['fields']['work_done'],
                        datetime.strptime(record['fields']['status_changed_on'], "%Y-%m-%d")
                            if record['fields']['status_changed_on'] else None,
                        record['fields']['duration_source'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links']['release_id'],
                        record['links']['project_id'],
                        record['links'].get('initiative_id'),
                        record['links']['created_by_user_id'],
                        record['links']['workflow_status_id'],
                    ))
                elif record['class'] == 'Initiative':
                    db.write_record(initiative_dml, (
                        record['id'],
                        record['fields']['reference_num'],
                        record['fields']['name'],
                        record['fields']['color'],
                        record['fields']['position'],
                        record['fields']['value'],
                        record['fields']['effort'],
                        record['fields']['presented'],
                        datetime.strptime(record['fields']['start_date'], "%Y-%m-%d")
                            if record['fields']['start_date'] else None,
                        datetime.strptime(record['fields']['end_date'], "%Y-%m-%d")
                            if record['fields']['end_date'] else None,
                        record['fields']['progress'],
                        record['fields']['progress_source'],
                        record['fields']['duration_source'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links']['project_id'],
                        record['links'].get('epoch_id'),
                        record['links']['workflow_status_id'],
                    ))
                elif record['class'] == 'Epoch':
                    db.write_record(epoch_dml, (
                        record['id'],
                        record['fields']['name'],
                        record['fields']['archived'],
                        datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
                        record['links']['account_id'],
                    ))

            db.batch_commit()

        # Event-based
        # for prefix, event, value in parser:
        #     if (prefix, event) == ("records.item", "start_map"):
        #         i += 1
        #     elif (prefix, event) == ("records.item.class", "string"):
        #         classes.add(value)
        #     elif (prefix, event) == ("records.item", "end_map"):
        #
        #         if i % 100000 == 0:
        #             logger.info(f"Processed {i} records")

        logger.info(f"Processed {i} records")

        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        logger.info(f"Found {len(sorted_classes)} classes")
        logger.info(f"{json.dumps(sorted_classes, indent=4)}")

    logger.info("Process complete")
