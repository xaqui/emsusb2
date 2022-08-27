# About
This is a script that picks up and binds input from the EMS USB2 ps2 to usb adapter for Joypads/Dance mats. Originally made by [tb2097](https://github.com/tb2097), this is a continuation of the original work.
The script takes the usb input and hard-codes it to keyboard keys using the following scheme:
|                |Player 1                       |Player 2                       
|----------------|-------------------------------|-----------------------------|
|Start           |Enter            				 |\[   						   |
|Select          |Backspace         			 |\]       					   |
|Left            |Left Arrow					 |Numpad 4  				   |
|Up				 |Up Arrow						 |Numpad 8					   |
|Right			 |Right Arrow					 |Numpad 6	     			   |
|Down			 |Down Arrow					 |Numpad 2					   |
|UpLeft			 |A                              |Numpad 7					   |
|UpRight		 |B								 |Numpad 9					   |
|DownLeft		 |C 							 |Numpad 1				       |
|DownRight	     |D								 |Numpad 3					   |

## Dependencies
* Python
	* Requires pywinusb module `pip install pywinusb`
	* Requires pywin32 module `pip install pywin32`

* You might need [EMS USB2 drivers](http://www.hkems.com/product/ps2/ps2-usb2.htm)

## Known issues
Older software sometimes struggles picking inputs from both players, if at all. Unfortunately this has to be fixed on a per case basis, since we haven't found any recurring or common problems.
If the USB device is disconnected during execution the program has to be launched again to resume picking up inputs. 

## Credits
* [tb2097](https://github.com/tb2097): Original author
* [iluminacos](https://github.com/iluminacos): Collaborator
* [xaqui](https://github.com/xaqui): Collaborator