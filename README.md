
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
1. The user begins the process by either scanning the QR code with a device or manually inputing the filament token in the system;
2. The user fills out details for the new filament roll e.g. manufacturer name, material type, stock weight, leftover weight and color;
3. the system registers the changes, and logs the new filament roll.