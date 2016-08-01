#Settlers of Planet Catan (3D Catan)

##Author
The program was written by Sean D Kim for 15-112 Term Project. The course is taught by David Kosbie and David Anderson at Carnegie Mellon University. 

##How to Run
You need to have python installed. You can install python at <https://www.python.org/downloads/>
To play the game, open the “3D Catan.py” file with python. The following items need to be in the same directory. Do not rename these files/folders. 
* eventBasedAnimation.py
* eventBasedAnimation.pyc
* icosahedron.obj
* images (folder of three images: alien.gif, space.gif, tile.gif)
* structClass.py
* structClass.pyc

If damaged, the files can be downloaded from following link 
* eventBasedAnimation: <http://www.cs.cmu.edu/~112/notes/notes-oop.html>
* structClass: <http://www.cs.cmu.edu/~112/notes/notes-oop.html>
* icosahedron.obj <http://people.sc.fsu.edu/~jburkardt/data/obj/icosahedron.obj>

##Objective
Whoever gets 10 points before another player wins. You can get point by building…

* House (Triangle): Wood, Brick, Sheep, Wheat (1 Point)
* City (Square): Ore, Ore, Ore, Wheat, Wheat (2 Points)
* Special Cards: Ore, Sheep, Wheat 
	* Victory point (1 point)
	* Knight (0 point): removes the alien on the board. 
	* Monopoly (0 point): Steal one type of resource from another player’s hand
	* Invention (0 point): Obtain two free resources of your choice. 
* Largest Army (2 points): obtained if the number of times a player used knights is 3 or more and bigger than that of another play. 


##Info
The program is an adaptation of an existing board game, Settlers of Catan. The board was adapted to a 3D-icosahedron board instead of original 2D board. Because the new board has less vertices, the game was modified into 2-player board game. All the rule of original Catan game applies except few exceptions:

* Less vertices on board => only two players at a game
* No Roads: house/city can be build anywhere
* Alien: When 7 is rolled, randomly blocks one tile; no stealing
* Knight: knight removes any alien on the board; no stealing
* No Trading Ports: All resources are traded 4:1 ratio with bank

To access the complete guide to the original Settlers of Catan,
go to <www.catan.com/service/game-rules>


##Features 
Start screen
* Select a color of your choice. Game starts when start button is pressed. 

Playing screen
* Set-up:
	* Help button: Click to view a help text. 
	* Click on a vertex of the board to build each of your two houses. 
	* Press arrow key to rotate the board
* Playing: 
	* Help button: Click to view a help text. 
	* Main Screen
		* Press arrow key to rotate the board
		* You can visually see the status of the board. 
		* Houses are represented by triangles, Cities by squares
		* White circle is drawn around the rolled number
		* You can see on which tile alien appeared
	* Navigation (top left)
		* Click Roll to roll the dice. 
		* Click Trade to trade cards. The trade window will pop up for trading. 
		* Click Build to build house/city or draw special cards
			* House Button: You can build a new house if you have enough 				resources. Click on this button and click on a vertex you want to 				build your new house. 
			* City Button: You can upgrade a house to a city if you have enough 				resources. Click on this button and click on a house you want to 				upgrade. 
		* Click End to end your turn. 

	* Widget (top right)
		* displays the following information of each player
			* Points: number of points (need 10 points to win)
			* Cards: number of resource cards
			* Specials: number of special cards
			* Knights: number of knights card used. (need at least 3 for largest Army)

	* Bar (bottom)
		* This is where your cards are displayed. 
		* Resources cards from left; Special cards from right

	* Sub-window (middle, under special circumstance)
		* This window appears during trade or when invention/monopoly is used. 
		* During trading:
			* Select resource you wish to obtain
			* Select four cards of a same kind
			* Press Confirm to trade these cards. 
			* Press Cancel to cancel trade. 
		- Invention:
			* select two resources you wish to obtain
			* Press Confirm to obtain these cards. Invention cards will disappear
			* Press Cancel to cancel. Invention card will NOT disappear. 
		* Monopoly:
			* select one resources you wish to obtain
			* Press Confirm to obtain all cards of selected type from computer. 				Monopoly cards will disappear. 
			* Press Cancel to cancel. Monopoly card will NOT disappear. 
	
	* cheatKeyDemo (not part of a game)
		* You can press these keys to obtain the following…
			* b => brick
			* i => invention
			* k => knight
			* l => any special card
			* m => monopoly
			* o => ore
			* s => sheep
			* t => wheat
			* v => victory point
			* w => wood
			

* Game-over: 
	* You can click “r” to play the game again. 



