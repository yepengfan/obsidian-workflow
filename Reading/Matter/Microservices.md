## Metadata
* URL: [https://martinfowler.com/articles/microservices.html](https://martinfowler.com/articles/microservices.html)
* Publisher: Martin Fowler
* Published Date: 2014-03-26
* Tags: 

## Highlights
* Monolithic applications can be successful, but increasingly people are feeling frustrations with them - especially as more applications are being deployed to the cloud . Change cycles are tied together - a change made to a small part of the application, requires the entire monolith to be rebuilt and deployed.
* Componentization via Services
* One main reason for using services as components (rather than libraries) is that services are independently deployable.
* Another consequence of using services as components is a more explicit component interface.
* Using services like this does have downsides. Remote calls are more expensive than in-process calls, and thus remote APIs need to be coarser-grained, which is often more awkward to use.
  * **Note**: Due to the high cost of remote calls, it is generally recommended to design remote APIs as coarser-grained interfaces. This means that each API call takes on more functionality and responsibility instead of implementing many fine-grained features. For example, a remote API call may need to pass a lot of data and perform multiple operations, while a local function call can break tasks down into finer granularity.
* Organized around Business Capabilities
* The microservice approach to division is different, splitting up into services organized around business capability.
* Products not Projects
* Smart endpoints and dumb pipes
* The biggest issue in changing a monolith into microservices lies in changing the communication pattern.
* Decentralized Governance
* Decentralized Data Management
* Using transactions like this helps with consistency, but imposes significant temporal coupling, which is problematic across multiple services. Distributed transactions are notoriously difficult to implement and as a consequence microservice architectures emphasize transactionless coordination between services, with explicit recognition that consistency may only be eventual consistency and problems are dealt with by compensating operations.
* Infrastructure Automation
* Design for failure
* A consequence of using services as components, is that applications need to be designed so that they can tolerate the failure of services. Any service call could fail due to unavailability of the supplier, the client has to respond to this as gracefully as possible.
* Evolutionary Design
* The key property of a component is the notion of independent replacement and upgradeability - which implies we look for points where we can imagine rewriting a component without affecting its collaborators.
