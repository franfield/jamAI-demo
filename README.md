# JamAI - An AI Tool For Guitarists
Ever want to play a solo and unsure where to start? I've been there. Use this tool to upload a screenshot of some chords and get back guitar tablature along with instructions on how to solo.
## Demo Instructions
1. Find the deployed project here: http://jam-ai.s3-website-us-east-1.amazonaws.com/
2. Use an image in the testcases/ directory or provide your own. Please make sure to use a .png or .jpeg and avoid including spaces or special characters in the filename.
3. Upload the image and click 'Process' (this is running on a Lambda so please be patient - it may need to cold start)
4. Enjoy!

## Application Components
### 1. Processing Lambda (This repo)
This application works by fetching the screenshots from an S3 bucket. First, it uses pytesseract to extract the text from the image. Then, it uses a Few Shot Prompt and the OpenAI API to create the JSON response expected by the UI. Finally, the response is created by parsing over the LLM response and generating pre-signed S3 URLs for each of the needed scales. The scale TXT files which are held in a separate S3 bucket and rendered by the UI.
### 2. Frontend
A simple static website built using React and hosted on S3
### 3. Scale Generator
All .txt files rendered by the UI were generated dynamically using Python.
### 4. Deployment Scripts
All components were deployed on AWS using CloudFormation scripts. Services used: API Gateway, S3, Lambda. 