for ui part
terminal 1: npm run start -- --host 0.0.0.0 --allowed-hosts
terminal 2: npx cloudflared tunnel --url http://localhost:4200 then type yes

for api part
terminal 1: uvicorn main:app --host 0.0.0.0 --port 8000
terminal 2: npx localtunnel --port 8000 --subdomain [subdomain_name]
