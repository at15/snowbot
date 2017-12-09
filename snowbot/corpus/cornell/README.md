# Cornell Movie Dialog Corpus

- https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html

## Preprocess

- [#15](https://github.com/at15/snowbot/issues/15) after observing the file, I found I am splitting QA in the wrong way, [L1, L2, L3] does not mean [u1, u2, u3]
  - https://github.com/b0noI/dialog_converter seems to be doing it the right way, I initially though he didn't find the conversation file

Following description is from [kaggle][kaggle]

- movie_titles_metadata.txt
	- contains information about each movie title
	- fields: 
		- movieID, 
		- movie title,
		- movie year, 
	   	- IMDB rating,
		- no. IMDB votes,
 		- genres in the format ['genre1','genre2',É,'genreN']

- movie_characters_metadata.txt
	- contains information about each movie character
	- fields:
		- characterID
		- character name
		- movieID
		- movie title
		- gender ("?" for unlabeled cases)
		- position in credits ("?" for unlabeled cases) 

- movie_lines.txt
	- contains the actual text of each utterance
	- fields:
		- lineID
		- characterID (who uttered this phrase)
		- movieID
		- character name
		- text of the utterance

- movie_conversations.txt
	- the structure of the conversations
	- fields
		- characterID of the first character involved in the conversation
		- characterID of the second character involved in the conversation
		- movieID of the movie in which the conversation occurred
		- list of the utterances that make the conversation, in chronological 
			order: ['lineID1','lineID2','lineIDN']
			has to be matched with movie_lines.txt to reconstruct the actual content

- raw_script_urls.txt
	- the urls from which the raw sources were retrieved
	
[kaggle]: https://www.kaggle.com/Cornell-University/movie-dialog-corpus