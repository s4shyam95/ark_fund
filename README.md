## Inspiration
Current crowd-funding platforms can be expensive and tough for newer companies to be “accepted” in. This led us to create a decentralised version for the same to offer companies to run standard crowd-funding campaigns and ICO while removing the expensive “middleman”.

## What it does
It provides Investors and Investees alike with a platform to find exciting campaigns and token offerings on the platform, whereas Investees get a chance to get their idea out there to a large network of investors.

## How we built it
We used Ark’s RPC to create 2 independent private ledgers. One is used as our applications’s database, to manage permissions, and tokens. The other is any old currency network (we used ARK). We use these 2 together with a cherrypy backend and django client app (MacOS) to allow users to launch and fund campaigns effortlessly.

## Challenges we ran into
We had a tough time setting up our private nets on Azure, but were able to get it up. Other then that the we faced slight issues of missing documentation with the Ark python client, but it wasn’t too tough to navigate their codebase and set it up.

## Accomplishments that we’re proud of
We are really proud of introducing a independent transaction chain which integrates into the app, it allows us to verify transfer of funds into an escrow on our network. It was also challenging but fun to have a private net, as it significantly improves speeds for requests to the blockchain.
Most of all, we are proud of being able to provide a platform for startups which can save upto 15% of transaction/platform fees they would end up paying otherwise.

## What we learned
Though we have worked with blockchain before, this was our first time with Ark, and it was really exciting. We got to know their architecture and API well. We also learned about crowd-funding options over the blockchain like Crypto-tokens.

## What’s next for ArkFund
We will have much much more flexibility once the Ark team is out with their VMs on nodes, allowing us to deploy smart contracts, removing further elements of trust and making the crowd-funding experience even more smooth.
Message Input

Message Shyam, ankush

*bold* _italics_ ~strike~ `code` ```preformatted``` >quote