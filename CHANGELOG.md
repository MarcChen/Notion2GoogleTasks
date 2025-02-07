## [0.0.2] - 2024-12-22
- Merged PR #4 by @MarcChen: FIX : versioning job on previous PR


## [0.0.3] - 2024-12-22
- Merged PR #6 by @MarcChen: Fix deployment errors by using Poetry for script execution
Update script execution commands to use Poetry, resolving previous deployment issues.

## [1.0.0] - 2024-12-22
- Merged PR #7 by @MarcChen: Release V1.0.0: Initial deployment of synchronizer
This pull request includes a version update for the notion-sync project. The change updates the version number from 0.1.0 to 1.0.0 in the pyproject.toml file. This update is to correct a previous pull request where the bump versioning did not work as expected.

Changes:
[pyproject.toml](https://github.com/MarcChen/Notion2GoogleTasks/compare/main...dev/deploy-services-to-github-action): Updated the project version from 0.1.0 to 1.0.0.

## [1.0.1] - 2024-12-22
- Merged PR #9 by @MarcChen: fix both previous workflow issue


## [1.0.2] - 2024-12-22
- Merged PR #15 by @MarcChen: fix : still trying to fix bump version expansion issue
For instance, with previous PR, this was the reason it failed : 

> ### Environment Variables Cleanup:
>   * [](diffhunk://#diff-83053cdd58e4c1fa71b292dfec284[6](https://github.com/MarcChen/Notion2GoogleTasks/actions/runs/12455742423/job/34769019982#step:6:6)007b3cbabe2c9253a530466441d9f5c2feL17-L20): Removed optional variables  and .

## [1.0.3] - 2024-12-22
- Merged PR #16 by @MarcChen: fix previous PR : worked out but removed the content of backticks 
For instance, with previous PR, this was the reason it failed : 

> ### Environment Variables Cleanup:
>   * [](diffhunk://#diff-83053cdd58e4c1fa71b292dfec284[6](https://github.com/MarcChen/Notion2GoogleTasks/actions/runs/12455742423/job/34769019982#step:6:6)007b3cbabe2c9253a530466441d9f5c2feL17-L20): Removed optional variables  and .

## [1.0.4] - 2024-12-22
- Merged PR #17 by @MarcChen: fix previous MR, content between backticks was removed
Still testing with the following PR body content

> ### Environment Variables Cleanup:
>   * [](diffhunk://#diff-83053cdd58e4c1fa71b292dfec284[6](https://github.com/MarcChen/Notion2GoogleTasks/actions/runs/12455742423/job/34769019982#step:6:6)007b3cbabe2c9253a530466441d9f5c2feL17-L20): Removed optional variables  and .

## [1.0.5] - 2024-12-22
- Merged PR #18 by @MarcChen: fix previous MR, content between backticks was removed
> ### Environment Variables Cleanup:
>   * [`.env_template`](diffhunk://#diff-83053cdd58e4c1fa71b292dfec284[6](https://github.com/MarcChen/Notion2GoogleTasks/actions/runs/12455742423/job/34769019982#step:6:6)007b3cbabe2c9253a530466441d9f5c2feL17-L20): Removed optional variables `FREE_MOBILE_PASS` and `FREE_MOBILE_USER`.

## [1.0.6] - 2024-12-22
- Merged PR #19 by @MarcChen: fix : due date not matching
The due date in the description doesn't align with the one in Notion. This discrepancy arises because I use an offset system: if the due date in Notion is too far in the future, I prefer to set the task date to today. To manage this, I maintain a secondary date specifically for setting the task date

---
# Copilot Genreated Summary 

This pull request includes several changes to the `sync_notion_google_task` service and its integration tests. The most important changes include adjustments to the due date handling in the synchronization method, updates to the integration test setup, and improvements to the validation logic.

### Changes in `sync_notion_google_task` service:

* Adjusted the due date handling in `sync_pages_to_google_tasks` method by introducing `recomputed_due_date` to ensure tasks are dealt with promptly. (`services/sync_notion_google_task/main.py`) [[1]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2L38-R43) [[2]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2L72-R77)

### Changes in integration tests:

* Improved the validation logic in the integration test to fetch and parse Notion pages and validate synchronization with Google Tasks. (`tests/integration/test_notion_to_google_syncer_integration.py`)

## [1.0.7] - 2024-12-25
- Merged PR #20 by @MarcChen: fix : patch due_date type error
Patch to fix this issue : 

> Processing Page: licence FFA 2024/2025 ou ton attestation PPS - SEMI  (ID: 597)
>   Task List ID for tag 'Travail': c0RkZFdiSm9NQnJ0c2d0aA
> Error building task description: 'str' object has no attribute 'strftime'

This pull request includes changes to the `services/sync_notion_google_task` service and its corresponding unit tests to handle due dates as strings instead of `datetime` objects. The most important changes are the modification of the `build_task_description` method and the corresponding updates to the unit tests.

Changes to due date handling:

* [`services/sync_notion_google_task/main.py`](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2L121-R121): Modified the `build_task_description` method to accept `due_date` as a string and convert it to a `datetime` object within the method. [[1]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2L121-R121) [[2]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2R144)

Updates to unit tests:

* [`tests/unit/test_notion_to_google_syncer.py`](diffhunk://#diff-ae32bc452849d064a1b9c50ca3ab1c54dffd8610b3b2b610dc56ab68c9497f6aL25-R25): Adjusted the `due_date` parameter to be a string in the `test_build_task_description` method and updated assertions to reflect this change. [[1]](diffhunk://#diff-ae32bc452849d064a1b9c50ca3ab1c54dffd8610b3b2b610dc56ab68c9497f6aL25-R25) [[2]](diffhunk://#diff-ae32bc452849d064a1b9c50ca3ab1c54dffd8610b3b2b610dc56ab68c9497f6aL34-R34)

## [1.1.0] - 2024-12-25
- Merged PR #21 by @MarcChen: Feat : adding freemobile sms alert
When syncing Notion and Google Tasks, the system already ensures resilience by continuing the sync process even if one page fails to sync. However, the issue was that I wasn’t informed of these failures since the GitHub Action didn’t fail. To address this, I’ve added a feature that sends an alert via my mobile provider's API whenever a sync failure occurs, ensuring I stay informed while maintaining system resilience.

---
This pull request introduces SMS alert functionality for error notifications in the Notion to Google Tasks synchronization process. The most important changes include adding new environment variables, updating the sync process to send SMS alerts, and implementing and testing the SMS API client.

### SMS Alert Functionality:

* [`.env_template`](diffhunk://#diff-83053cdd58e4c1fa71b292dfec2846007b3cbabe2c9253a530466441d9f5c2feR17-R21): Added `FREE_MOBILE_USER_ID` and `FREE_MOBILE_API_KEY` as optional environment variables for SMS alerts.
* [`.github/workflows/sync_notion_to_google.yml`](diffhunk://#diff-4d0c7cedac148f0b4c03700fe8bc7320da1eca7be59c69a395cc88af4df828a9R110-R111): Updated the GitHub Actions workflow to include the new SMS alert environment variables.
* [`main.py`](diffhunk://#diff-b10564ab7d2c520cdd0243874879fb0a782862c3c902ab535faabe57d5a505e1R9-R19): Added retrieval and assertion of the new SMS alert environment variables.
* [`services/sync_notion_google_task/main.py`](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2R10-R16): Integrated `SMSAPI` into the `NotionToGoogleTaskSyncer` class to send SMS alerts on errors during the sync process. [[1]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2R10-R16) [[2]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2R64) [[3]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2R73) [[4]](diffhunk://#diff-ca3291ce30ba1de4e7c6d1b01581005f2532cba798ef777740f965964fb2c3e2R86)

### SMS API Client Implementation:

* [`services/free_sms_alert/main.py`](diffhunk://#diff-8fab397c4efab579ad00e5c12aa6e0a6796d3491f39f5542728080039cad0c2dR1-R97): Implemented the `SMSAPI` class to handle sending SMS messages, including error handling for various HTTP response codes.

### Testing:

* [`tests/README.md`](diffhunk://#diff-dacac2ebf9792f0d23c0f922a744486ded01901957d5281290925acd89cf83acL27-R81): Updated the README to include new unit and integration tests for the SMS alert functionality.
* [`tests/integration/test_alert_sms_integration.py`](diffhunk://#diff-7b32783bf259b4204713152d6fcb341669a00c5325bc87669c5512f4572ecf6aR1-R25): Added integration tests for the `SMSAPI` class to verify SMS sending with real credentials.
* [`tests/unit/test_alert_sms_free.py`](diffhunk://#diff-5d0b4faa3e361bb96379e32c6bcac20ac1ef80c67a6fdb3b03f3804e0bb1971cR1-R35): Added unit tests for the `SMSAPI` class to test successful SMS sending and error handling.

## [1.1.1] - 2024-12-26
- Merged PR #22 by @MarcChen: Fix/workflow on new machine
This pull request addresses issues with the `.github/workflows/sync_notion_to_google.yml` file, specifically to ensure the workflow functions correctly even if the runner is not pre-configured. Previously, the workflow failed when the environment was not fully set up from scratch. These changes aim to improve reliability and usability.

---

### Workflow improvements:

- **Branch condition**: Added a condition to execute the workflow only on the `main` branch. (`.github/workflows/sync_notion_to_google.yml`)

### Python installation process:

- **Updated method**: Updated the installation process for Python 3.10 to use the `deadsnakes` PPA and ensured the PATH is correctly set. (`.github/workflows/sync_notion_to_google.yml`)

### Poetry installation process:

- **PATH export**: Added a step to export Poetry's bin directory to PATH for the current session and ensured the PATH is correctly set. (`.github/workflows/sync_notion_to_google.yml`)

### Error messaging:

- **Improved checks**: Enhanced error messages for Python 3.10 and Poetry installation steps to provide better clarity. (`.github/workflows/sync_notion_to_google.yml`)

## [2.0.0] - 2025-02-01
- Merged PR #25 by @MarcChen: Feature : Enhanced Synchronization, Documentation, and Refactoring for Notion2GoogleTasks
This pull request includes several significant changes across multiple files to enhance the functionality and maintainability of the Notion2GoogleTasks project. The most important changes include the addition of new workflow steps, updates to documentation, and code refactoring for better readability and functionality.

### Workflow Enhancements:
* [`.github/workflows/sync_notion_to_google.yml`](diffhunk://#diff-4d0c7cedac148f0b4c03700fe8bc7320da1eca7be59c69a395cc88af4df828a9R6-R8): Added steps to install `jq` for JSON parsing and retrieve the last successful sync time to ensure proper synchronization between Notion and Google Tasks. [[1]](diffhunk://#diff-4d0c7cedac148f0b4c03700fe8bc7320da1eca7be59c69a395cc88af4df828a9R6-R8) [[2]](diffhunk://#diff-4d0c7cedac148f0b4c03700fe8bc7320da1eca7be59c69a395cc88af4df828a9L93-R125) [[3]](diffhunk://#diff-4d0c7cedac148f0b4c03700fe8bc7320da1eca7be59c69a395cc88af4df828a9L105-R137) [[4]](diffhunk://#diff-4d0c7cedac148f0b4c03700fe8bc7320da1eca7be59c69a395cc88af4df828a9R150-R151)

### Documentation Updates:
* [`.github/issue_template.md`](diffhunk://#diff-13908ed03c30afd7f2dd929641a43331db108751b927a5683b87eaec100bd305R1-R27): Added a new issue template to standardize issue reporting.
* [`CODE_OF_CONDUCT.md`](diffhunk://#diff-ffdbe3a1e7ee93cacfc080b6c635ccf3a8f6b0f00f2fb884f78c6b5f9dac8fd2R1-R79): Introduced a Contributor Covenant Code of Conduct to promote a positive community environment.
* [`CONTRIBUTING.md`](diffhunk://#diff-eca12c0a30e25b4b46522ebf89465a03ba72a03f540796c979137931d8f92055R1-R37): Added a contributing guide to help new contributors understand the process of contributing to the project.
* [`TODO.md`](diffhunk://#diff-5c6a1301c6b59b30a040d747d065e861d3dd98bde0e5a4356d92d594e9835986R1-R26): Created a TODO list outlining tasks required for the V2 version of the project.
* [`flowchart.md`](diffhunk://#diff-734e84eaf48b72d04874c9056b4cca95bcf0c2c82d1da9677b183433ce497bfdR1-R137): Added a detailed flowchart for the Google Tasks and Notion sync process to provide a clear understanding of the synchronization workflows.

### Code Refactoring:
* [`main.py`](diffhunk://#diff-b10564ab7d2c520cdd0243874879fb0a782862c3c902ab535faabe57d5a505e1R2-R3): Refactored to include the `last_successful_sync` environment variable and ensure proper initialization and synchronization processes. [[1]](diffhunk://#diff-b10564ab7d2c520cdd0243874879fb0a782862c3c902ab535faabe57d5a505e1R2-R3) [[2]](diffhunk://#diff-b10564ab7d2c520cdd0243874879fb0a782862c3c902ab535faabe57d5a505e1R13-R43)
* [`services/free_sms_alert/main.py`](diffhunk://#diff-8fab397c4efab579ad00e5c12aa6e0a6796d3491f39f5542728080039cad0c2dL1-R32): Improved code readability by adding spacing and reformatting long lines. [[1]](diffhunk://#diff-8fab397c4efab579ad00e5c12aa6e0a6796d3491f39f5542728080039cad0c2dL1-R32) [[2]](diffhunk://#diff-8fab397c4efab579ad00e5c12aa6e0a6796d3491f39f5542728080039cad0c2dL63-R71) [[3]](diffhunk://#diff-8fab397c4efab579ad00e5c12aa6e0a6796d3491f39f5542728080039cad0c2dL86-R101)
* [`services/google_task/config/config_creds.py`](diffhunk://#diff-32b8b4d07c2a49513219ca7b2582a797a670c0d3113995b890a66c4feca4c430L1-R4): Refactored import statements and improved argument parsing for better readability. [[1]](diffhunk://#diff-32b8b4d07c2a49513219ca7b2582a797a670c0d3113995b890a66c4feca4c430L1-R4) [[2]](diffhunk://#diff-32b8b4d07c2a49513219ca7b2582a797a670c0d3113995b890a66c4feca4c430L13-R14) [[3]](diffhunk://#diff-32b8b4d07c2a49513219ca7b2582a797a670c0d3113995b890a66c4feca4c430L23-R39)

## [2.0.1] - 2025-02-01
- Merged PR #26 by @MarcChen: fixing workflow issue
# Bump Version to 2.0.0 and Fix Failing Workflow Executions

This pull request primarily bumps the project version to 2.0.0 and addresses failing executions in the GitHub Actions workflow. Below is a summary of the main changes:

## Workflow Configuration Updates

- Updated the .github/workflows/sync_notion_to_google.yml file to fix failing workflow steps and ensure the Poetry environment uses Python 3.10 correctly.
- Adjusted steps to run commands with python instead of python3.10.

## Script Improvements

- Refined console output messages in services/sync_notion_google_task/main.py to display page IDs rather than page titles.
- Removed superfluous print statements for cleaner output.

## Code Cleanup

- Removed an extra print statement for token TTL in services/google_task/src/authentification.py to streamline the function.
- By updating to version 2.0.0, these changes lay the groundwork for a more reliable workflow execution process and cleaner code output.








## [2.0.2] - 2025-02-04
- Merged PR #28 by @MarcChen: fix : duplicated created tasks 
### Fix: Duplicated Created Tasks

This pull request addresses an issue where tasks were being duplicated during synchronization between Notion and Google Tasks. The fix introduces a new mechanism to mark pages that originate from tasks by adding a `FromTask` checkbox property in Notion. This property helps prevent redundant task creation during sync operations.

#### Key Changes:

- **Notion Client Updates:**
  - **`create_new_page` Method:**  
    An optional `from_task` parameter has been added to set the `FromTask` checkbox when creating a new page in Notion.
  - **`parse_notion_response` Method:**  
    Updated to extract the `FromTask` checkbox value from Notion’s response, ensuring that the task origin is correctly tracked in the parsed data.

- **Synchronization Logic Updates:**
  - **`sync_pages_to_google_tasks` Method:**  
    Modified to skip pages where the `FromTask` checkbox is enabled, preventing the creation of duplicate tasks during synchronization.
  - **`print_progress` Method:**  
    Now creates new Notion pages with the `FromTask` checkbox set to `True` when tasks are being synchronized from Google Tasks, ensuring the origin is properly flagged.

This fix ensures that tasks originating from Google Tasks are not re-created in Notion during subsequent syncs, effectively eliminating the duplication issue.

