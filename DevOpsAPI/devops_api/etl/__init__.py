from datetime import datetime
import json

PROJECT = """
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

IDEA = """
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

USER = """
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

RELEASE = """
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

FEATURE = """
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

REQUIREMENT = """
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

INTEGRATION = """
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

EPIC = """
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

INITIATIVE = """
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

EPOCH = """
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


def record_to_sql(record, db):
    """
    To setup db connection:
    ```
        with SqlWriter(driver=SQL_DRIVER,
                       host=SQL_HOST,
                       db=SQL_DB,
                       uid=SQL_USER,
                       pwd=SQL_PWD) as db:
        ...
        db.batch_commit()
    ```

    :param record:
    :param db:
    :return:
    """
    if record['class'] == 'Project':
        db.write_record(PROJECT, (
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
        db.write_record(IDEA, (
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
        db.write_record(USER, (
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
        db.write_record(RELEASE, (
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
        db.write_record(FEATURE, (
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
        db.write_record(REQUIREMENT, (
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
        db.write_record(INTEGRATION, (
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
        db.write_record(EPIC, (
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
        db.write_record(INITIATIVE, (
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
        db.write_record(EPOCH, (
            record['id'],
            record['fields']['name'],
            record['fields']['archived'],
            datetime.strptime(record['fields']['created_at'], "%Y-%m-%d %H:%M:%S %Z"),
            datetime.strptime(record['fields']['updated_at'], "%Y-%m-%d %H:%M:%S %Z"),
            record['links']['account_id'],
        ))
