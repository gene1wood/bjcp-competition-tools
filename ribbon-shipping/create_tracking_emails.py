import json

with open('labels.json') as f:
    winners = json.load(f)

for email in winners:
    name = winners[email]['name'].split(' ')[0]
    from_address = f"{winners[email]['name']} <{email}>"
    url = f"https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1={winners[email]['tracking_code']}"
    body = f"""{from_address}

World Cup of Beer : Your ribbon(s) have been shipped

{name},
    Congratulations on your win(s) at the World Cup of Beer. I've put your ribbon(s) in the mail tonight and the package should show up in the USPS system tomorrow. You can track the shipment to know when it will arrive with this URL : 

{url}

Thanks again for competing and we hope to see your entries again in 2023!

-Gene Wood
Registrar, World Cup of Beer
"""
    print(body)