
# Filament Management System
## Concept
The concept of the filament management system is to organize existing and new filament rolls by registering them in the system with metadata. The metadata would consist of manufacturer name, material type, stock weight, leftover weight and color. The metadata would also be used with logging registry that shows the current filament usage, such as date, last printer used, last file name used for printing and weight used.

The filament management system would allow users to add a new filament roll and fill out basic required metadata. The metadata consists of two parts, where one part is registered by the system automatically, and the second part is filled out manually by the user. 

Each filament roll that is added to the system will have a generated unique token, that can be used to track and log the filament roll. Each token will have the ability to be printed out in QR code label format, so that it can be sticked to the actual filament roll. 

The QR code would allow for the user to accurately track the filament in the fulfillment process by scanning or manually inputting in the system whenever the filament roll is about to get used for printing. 


# Current features
* New filament roll registration ( automatic token generation, manual metadata input )
* Filament roll usage registration ( updates leftover weight, logs usage details )
* QR code generation
* QR code scanner ( currently inactive )


## Process description
### Adding a new filament roll
When a new filament roll is added to the system:
1. The user begins by filling out details about filament roll e.g. manufacturer name, material type, stock weight, leftover weight and color;
2. The user is asked to select/create a storage location for the filament roll;
3. the system registers the changes, and logs the new filament roll.

### Using a filament roll
When a filament roll is used for printing:
1. The user begins the process by either scanning the QR code with a device or manually inputing the filament token in the system from the available selection;
2. The user is asked to select/create the printer used for printing;
3. The user is asked to select/input the file name, weight used for printing;
4. The system registers the changes, and logs the usage details.

# Revenue model
SaaS/Subscription based ( monthly fee )
The subscription will provide access to the following features:

* Unlimited storage of filament rolls
* Unlimited storage of usage logs
* Unlimited storage of printing history
* Access to all features of the system, including QR code generation and scanner

## Subscription Tiers
The subscription model will consist of three tiers:

* Basic - for hobbyists or individuals who only need to manage a few rolls of filament
* Pro - for small businesses or organizations with a moderate number of rolls to manage
* Enterprise - for larger businesses or organizations with a high volume of filament rolls to manage
Each tier will have a different monthly fee, with the Basic tier being the lowest and the Enterprise tier being the highest.

## Additional Revenue Streams
In addition to the subscription model, the filament management system could offer additional revenue streams, such as:

* Selling QR code labels for users who want to print and use them
* Offering premium support services for users who need assistance or troubleshooting
* Providing data analytics services to businesses who want to track their filament usage and optimize their printing processes
* Overall, the subscription model will provide a predictable monthly revenue stream for the filament management system, while the additional revenue streams will offer opportunities for further growth and expansion.