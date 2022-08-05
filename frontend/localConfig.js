export default {
  // Docs: https://axios.nuxtjs.org/options/#browserbaseurl
  // apiBaseURL is used for the server part of nuxt (running in node on server).
  // E.g. internal networking can be used on apiBaseURL for axios requests on server.
  // browserBaseURL will be used on axios requests which are ran on client=browser side.
  // browserBaseURL needs to be public reachable on the internet!
  apiBaseURL: process.env.API_URL || 'https://corgi-staging.ce.openstax.org',
  browserBaseURL: process.env.API_URL_BROWSER || 'https://corgi-staging.ce.openstax.org'
}
