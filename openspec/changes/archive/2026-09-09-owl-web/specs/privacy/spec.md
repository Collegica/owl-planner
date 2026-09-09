## MODIFIED Requirements

### Requirement: No network, no credentials
The tool SHALL make no network requests and SHALL require no bank credentials, API keys or accounts. Input is files the user exported themselves. In the browser, the web app SHALL make no request after its own assets have loaded, SHALL load those assets only from the site that serves the page, and SHALL keep personal files in the user's own browser storage and memory only.

#### Scenario: Offline run
- **WHEN** the machine has no network connection
- **THEN** `pixi run budget` completes normally

#### Scenario: Browser run after load
- **WHEN** the web app has loaded and the network is then disconnected
- **THEN** dropping files, editing configuration and running all complete normally

#### Scenario: Assets are first-party
- **WHEN** the page loads on the Collegica site
- **THEN** every request is to the same origin as the page
