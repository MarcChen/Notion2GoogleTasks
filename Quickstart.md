# Quickstart Guide

## Setting Up API Keys

### Google Tasks API

1. Create a Google Account (e.g., `my.drive.app@gmail.com`) or use an existing account (this can be any account, it doesn't need to be the one used for Google Tasks).
2. Go to the [Google API Console](https://console.developers.google.com/apis/credentials/oauthclient?project=mydriveapp) and create a new project.
3. Navigate to `Credentials` and click `Create Credentials` > `OAuth Client ID`.
4. Select `Web application` and add `https://developers.google.com/oauthplayground` as an authorized redirect URI.
5. Note the `Client ID` and `Client Secret`.

6. Go to the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).
7. In the Settings (gear icon), set the following:
  - OAuth flow: Server-side
  - Access type: Offline
  - Use your own OAuth credentials: Check this option
  - Client ID and Client Secret: Use the values from step 5

8. Add Google Task Scopes.

9. Click "Authorize APIs". You will be prompted to choose your Google account (the one you'll synchronize Google Tasks with) and confirm access.

10. Click "Step 2" and "Exchange authorization code for tokens".

11. Note the `GOOGLE_ACCESS_TOKEN` and `GOOGLE_REFRESH_TOKEN`.

Update your `.env` file with the following values (for local dev):
```
GOOGLE_ACCESS_TOKEN=""
GOOGLE_REFRESH_TOKEN=""
GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
```

### Notion API
1. Visit [Notion Integrations](https://www.notion.so/my-integrations) and create a new integration.
2. Save the `Internal Integration Secret` provided by Notion.
3. Share your database with the integration:
    - Open the Notion database you want to connect.
    - Click on the three dots in the top-right corner.
    - In the Connection selector, choose the integration you just created.

4. Update your `.env` file with the following values:
    ```
    NOTION_API_KEY=""
    NOTION_DATABASE_ID=""
    ```

## Integrating with GitHub Actions

1. **Fork the Repository**:  
  Go to the [repository link](https://github.com/MarcChen/Notion2GoogleTasks/tree/main) and click on **Fork** in the top-right corner of the page.

2. **Set Up Secrets in Your Fork**:  
  - Go to your forked repository on GitHub.
  - Click on **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
  - Add the following secrets:
    - `GOOGLE_ACCESS_TOKEN`
    - `GOOGLE_REFRESH_TOKEN`
    - `GOOGLE_CLIENT_ID`
    - `GOOGLE_CLIENT_SECRET`
    - `NOTION_API_KEY`
    - `NOTION_DATABASE_ID`

3. **Set Up a Self-Hosted Runner**:  
  - Since scheduled workflows are disabled after 60 days of inactivity on the free tier, you need to set up a self-hosted runner.
  - Follow the [GitHub documentation](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners) to set up a self-hosted runner for your repository.

4. **Trigger the Workflow**:  
  - To test the workflow, go to the **Actions** tab in your repository and manually run the `Sync Notion to Google Tasks` workflow. Alternatively, the workflow is scheduled to run automatically at 8 AM, 12 PM, 4 PM, and 8 PM every day.
