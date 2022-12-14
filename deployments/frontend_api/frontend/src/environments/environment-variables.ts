export interface IEnvironmentVariables {
    // #region Properties (3)

    baseApiUrl?: string;
    baseUrl: string;
    environment: string;

    // #endregion Properties (3)
}


export class EnvironmentVariables {
    // #region Public Static Methods (1)

    /**
     * Returns a new object of type IEnvironmentVariables created by loading
     * values from window. This approach can be used to specify pseudo
     * environment variables that can be changed without rebuilding the
     * application. A placeholder file "environment.js" is included in index.html
     * for this purpose, by default the file is empty, but it can be overwritten
     * with code similar to the following:
     *
     * (function (window) {
     *      window.__environment = window.__environment || {};
     *      window.__environment.baseUrl = 'https://localhost:4200';
     *      window.__environment.environment = 'development';
     * }(this));
     *
     * One use case for this approach is to overwrite variables when running client
     * containers for development purposes (similar to container environment
     * variables).
     *
     * @param defaultVariables Default values to be used if not specified in window.
     * @returns A new object of type IEnvironmentVariables.
     */
    public static load(defaultVariables: IEnvironmentVariables): IEnvironmentVariables {
        const browserWindow = window as { [key: string]: any };
        const variables = browserWindow['__environment'] || defaultVariables;

        return variables;
    }

    // #endregion Public Static Methods (1)
}
