### How to Configure `token.json`

Follow these instructions:

1. Go to the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).
2. In the Settings (gear icon), set the following:
    - OAuth flow: Server-side
    - Access type: Offline
    - Use your own OAuth credentials: Check this option
    - Client ID and Client Secret: Use the values from step 5

3. Add Google Task Scopes.

4. Click "Authorize APIs". You will be prompted to choose your Google account and confirm access.

5. Click "Step 2" and "Exchange authorization code for tokens".

6. Update your `.env` file with the following values:
    ```
    GOOGLE_ACCESS_TOKEN=""
    GOOGLE_REFRESH_TOKEN=""
    GOOGLE_CLIENT_ID=""
    GOOGLE_CLIENT_SECRET=""
    ```

7. Source the `.env` file.

8. Execute the Python `config/config_creds.py`script to create the token that will be used.


Note: Moving tasks to a different task list isn't supported!

For more information, refer to the [Google Tasks API documentation](https://developers.google.com/resources/api-libraries/documentation/tasks/v1/python/latest/index.html).
