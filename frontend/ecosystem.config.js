module.exports = {
  apps: [
    {
      name: 'sedaily-eng',
      script: 'server.js',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev',
        REVALIDATE_SECRET: 'd5aed293ec4993ad6b13a4033b3b73986b40206cd6d6f43018b3ec0f01bc2748'
      },
    },
  ],
};
