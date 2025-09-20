<<<<<<< HEAD
# Trade Scan Pro Frontend (React)

This is the React SPA for Trade Scan Pro. It is deployed to a static webspace connected to `https://tradescanpro.com` and communicates with a separate Django backend over HTTPS.

## Environment Configuration

Copy `.env.example` to `.env` and set values before building:

```
REACT_APP_BACKEND_URL=https://api.tradescanpro.com
REACT_APP_API_PASSWORD=
REACT_APP_PAYPAL_CLIENT_ID=
```

Notes:
- `REACT_APP_BACKEND_URL` must point to the Django server base URL. All API calls go to `${REACT_APP_BACKEND_URL}/api` and revenue to `${REACT_APP_BACKEND_URL}/revenue`.
- `REACT_APP_API_PASSWORD` is optional and, if used, is sent as `X-API-Key` on requests.
- `REACT_APP_PAYPAL_CLIENT_ID` should be your PayPal public client id for the selected environment (sandbox or live).
- Values are embedded at build time; rebuild after changing.

## Routing on Static Hosting

The app uses hash-based routing (`HashRouter`) to ensure deep links work on static hosting without server rewrites. All links are of the form `/#/path`.
=======
# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

<<<<<<< HEAD
Deploy the `build/` directory to your static webspace for `tradescanpro.com`. Ensure environment variables were set prior to the build.

## Django Backend

The Django backend runs on a separate server and should be configured to allow CORS for the static origin. Typical base URL example: `https://api.tradescanpro.com`.

## Documentation

- In-app docs: navigate to `/#/docs`
- Glossary and quick start are provided and interlinked.

=======
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
