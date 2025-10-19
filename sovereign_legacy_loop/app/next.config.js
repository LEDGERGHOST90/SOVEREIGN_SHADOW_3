/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Config files are now in config/
  env: {
    CUSTOM_CONFIG_PATH: './config'
  }
}

module.exports = nextConfig
