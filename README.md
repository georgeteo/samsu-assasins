# Samsu Assasins

By: George Teo, Scarlett Li

Built for UChicago SAMSU assasins 2016. 
This project is licensed under the terms of the MIT license.

- Backend: Flask Rest Api	
- Mobile: Twilio

## Dev notes

Built with Google App Engine Python SDK.

```
// Dev server
dev_appserver.py .

// To upload a new version to app engine:
appcfg.py update .
```

## TODO

1. Unit test
2. Spy Function
3. Custom Control Panel
5. Push team -- TODO Comment in reply.py

## Testing TODO

Make all static methods into instance methods. :(

1. Handler.py routing of each command + Error command
3. REPLY.handler and subcommands -- Skeleton in test_reply.py
7. Action Error handling in Main.py -- TODO update error handling in '/' for new error types
8. Unknown Error handling in Main.py
9. Sending outoing messages to response num_list


- Test Bomb worker
- Test Invul worker
- Test Disarm worker



