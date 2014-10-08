# begintime = time()

Age
	How old are you? txtfield
Gender
	What is your gender? radio
Nationality
	What is your nationality? Dropdown (see nations.form)
Education
	What is the highest degree or level of school you have completed?
		* Did not finish High School
		* High School
		* Bachelor's Degree
		* Master's Degree
		* Doctoral Degree

	~ if post High School

		In which field? radio
			* Humanities
			* Natural Sciences
			* Engineering
			* Social Sciences
			* Economics
			* Arts
			* Other ____

Progamming experience
	Do you have any experience with computer programming/markup?
	radio: yes / no

	~ if yes

		Please indicate your programming level of proficiency? 1 meaning little experience, 
		6 meaning professional experience.
		radio: 1 - 6

		Please indicate which programming/markup languages you have experience using.
		checkboxes:
			* Java
			* JavaScript
			* Python
			* C/C#/C++
		 	* HTML
		 	* TeX/LaTeX
		 	* Markdown
		 	* RSS
		 	* Other ____

Excercises
# the order of the exercises should probably be randomized, to ensure validity from answers
# but generally, i think participants should make an Q1-type assignment before, a Q2-type
# so we don't put ideas in to their heads


The following questions are all related to how humans visually interpret computer languages,
and namly how a markup language should be designed.


Q1-type
# convert image to markup
Please make an identical representation of the image on the right using only plain text.

txtarea

Please explain your answer briefly: txtarea

Q2-type
# present markup, chose between (3) images
Please choose the image that you think represents the text best

Please explain your answer briefly: txtarea




# totaltime = time() - begintime
# store totaltime, so we can remove answers based on potentially invalid