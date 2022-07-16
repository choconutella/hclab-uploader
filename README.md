# hclab-uploader

**Python launcher application for  :** 
- Bridging within HCLAB and HIS
- Auto-email result
- API uploader


**How to use :**

1. Create new service in the services folder


2. Import the service 
```
from services.table_order import TableOrder
from services.table_result import TableResult
from services.cleanup import CleanUp
from services.email import Email
```

3. Add service to following thread's array
```
threads = [
  {"task" : "TableOrder", "title" : "Uploader Order"},
  {"task" : "TableResult", "title" : "Uploader Result"},
  {"task" : "Email", "title" : "Auto Email"},
  {"task" : "CleanUp", "title" : "Clean Up Manager"}
]
```

