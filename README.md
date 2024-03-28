# Arxiv-to-Zulip bot

## How to Setup
1. Fork this repository
2. Add secrets to your repository settings
  - For this go to your repository settings >> Secrets and Variables >> Actions >> New repository secret
  - Add `ZULIP_SITE` as the `https://yourdomainname.zulipchat.com` (replace `yourdomainname` with your domain name)
  - Add `ZULIP_EMAIL` as the email id for the bot
  - Add `ZULIP_API_KEY`. This you can get from the bot settings in zulip
3. Change `ARXIV_CATEGORIES` to your required categories in `main.py`
4. Set required interval to run the script using the cron expression in `.github/workflow/zulip-bot-workflow.yml`. [This website might help](https://crontab.cronhub.io/)
