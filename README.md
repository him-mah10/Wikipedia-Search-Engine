# Wikipedia Search Engine
Developed Search Engine for Wikipedia dump ( 64GB) using external merge sort with query time under 5s. Ranked results by calculating the relevance of the search query to results using tf-idf. Support for field queries was also there.


## How to run?
1. Open terminal and make a directory named 'data' using "mkdir data" command.
2. Create index using index.py file
   <br><b>Command -</b> python3 index.py <File whose index has to be created>
3. After index is created in data folder, run the search.py file to search 
	<br><b>Command -</b> python3 search.py
4. How to search?
	<br>Normal Search:
    <ul>
		<li>To do normal search, just type the keyword(s).
		  <li>To do field query?
			<br>field:keyword(s) field:keyword(s) ....
			<br>field can be any of ['title','body','infobox','category','ref','links','t', 'b', 'i', 'c', 'r', 'l']
		<li> To exit search engine just type exit()
