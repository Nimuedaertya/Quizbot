
Actually I wanted to get into the syntax of markdown, but hadn't the time for it.

So a few comments to the new bot:

- I tried implementing SQL
- init has to be called at first in discord
- afterwards it is not needed
- group works as before
- add does not need the role anymore
- reset clears database and also calls init

!init - creates database and needed evironment
!group TEAM - creates a role with name TEAM and adds writer to the team
!add MEM1 MEM2 MEM3 - adds members to the team of the author
!reset - clears all members of database and all channels 

Further updates incoming :) Maybe with markdown 


