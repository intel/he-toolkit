// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
import { EnvironmentVariables } from './environment-variables';

const environmentId = 'development';

const environmentVariables = EnvironmentVariables.load({
    baseUrl: 'http://localhost:4200',
    baseApiUrl: 'http://{IP_API_SERVER}:5000',
    environment: environmentId
});

const baseUrl = environmentVariables.baseUrl;
const baseApiUrl = environmentVariables.baseApiUrl || baseUrl;

export const environment = {
    production: false,

    urls: {
        siteUrl: baseUrl,

        auth: `${baseApiUrl}/auth`,

        apiJobs: `${baseApiUrl}/api/v1.0/jobs`,
    },
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
