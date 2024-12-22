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

