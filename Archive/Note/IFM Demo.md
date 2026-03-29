## Demo Branches

## Repositories
### infodrive-cx-api
`feature/CSIFS-001-incident-management`

### infodrive-cx-ui
`feature/CSIFS-001-incident-management`

## Current status
### Run the app on both BE & FE to see the current status
Only two dashboard items (Home & Performance Insights)
```
https://localhost.jisedai-internal.de:3000/
```
![[Pasted image 20260324093929.png]]
### Compare with the Mashi app on incident management flow
```
url: https://staging2.infodrivecx.com/mitsubishiau/dealer/index.jsp?logout=2
username: adminuser@ciandt.com
password: login01
```

#### Show CSI::Incidents interface
##### Steps
###### Find Incidents date from `01/03/2025` to today
![[Pasted image 20260324093758.png]]

###### Click on incident item to see the editable fields
![[Pasted image 20260324093907.png]]

## Trigger SDD
### Open Typora for a better view

```
/sdd:spec-init "CSI Incident Management"
/sdd:spec-requirements csi-incident-management
/sdd:validate-gap csi-incident-management
/sdd:spec-design csi-incident-management -y
/sdd:validate-design csi-incident-management
/sdd:spec-tasks csi-incident-management -y
/sdd:spec-impl csi-incident-management
```

## Run Tests
### CX-UI
```
yarn test
```
### CX-API
```
pytest -q --no-header
```