A month ago, I created this video to
demonstrate the power of longunning
harnesses for coding agents. And
initially, this was actually based on an
article written by Anthropic on an
effective harness for longunning agents.
The idea behind this is that we can get
agents to implement massive projects
containing hundreds of features. Now,
this is something that's simply not
doable with a single agent as the coding
agents will very easily reach the
context window limit. To demonstrate
this using cloth code, Anthropic even
gave us a sample project which you can
download and run on your own machine.
Now there are a few limitations and
issues with their implementation. One
limitation was that it doesn't have a UI
and the entire thing runs in the
terminal and it makes it very hard to
visualize what's going on behind the
scenes. So my intention in this video
was to simply create a UI on top of
Anthropics demo so you could see all of
the available features in a local
database and you can visualize the
progress in a canban board. But then
something unexpected happened. Since
releasing this application for free,
people started using it and they seem to
love it. The project currently has 1,300
stars on GitHub and is constantly
growing. We also have a vibrant
community of people who are contributing
feature ideas and even adding to the
repo. We've added tons of functionality
and quality of life improvements to this
application as well. And more
importantly, we renamed it to AutoForge.
In this video, I will show you how to
set it up on your own PC, which is
really easy by the way. And we will have
a look at all the available features in
this app, but at a very high level. You
can see that a project is currently
running and we've got about 25 features
to implement. And we have the scan band
board view where we can see all of the
pending features. We can see exactly
what features are currently being
implemented by the coding agents. And of
course, we can view all the features
that are done. If we click on any of
these cards, we can view the
dependencies between other features. We
can see the exact steps required in this
feature and we can edit these features
at any time. And we also have this graph
view which shows all these little
features and their dependencies with
each other. And we can also see which
agents are currently working on which
features. And if we expand mission
control, we can see exactly what the
orchestrator agent is doing as well as
each of the subcoding agents. And this
is also important. We actually have
multiple agents running concurrently to
work on different features at the same
time. By default, autoforge uses cla
code, but we also have support for the
GLM models as well as Ola. So if you
want to do free inference on your local
machine and we are rolling out support
for additional models and providers in
the near future. So let's have a look at
setting up AutoForge on your machine.
And yes, this platform is completely
free. To get started, I recommend going
to autoforge.cc.
This is where you can view all of the
documentation on getting started and
using all the available features in the
app. And if you would be so kind, you
can actually click on this GitHub
button. And if you like this project,
you can simply click on the star button.
And if we scroll down, we can see all of
the prerequisites like installing
NodeJS, the cloth code CLI, which is
needed for this project. And you will
also need to install Python as well.
Now, you basically have two options for
setting this project up. The easiest
solution is to simply run this command
in your command prompt or terminal.
These are the same instructions that
you'll find on the actual documentation.
So, simply copy this command, then run
that command in your command prompt or
terminal, and you only have to do the
installation once. By the way, to start
Autoforge, all you have to do is run the
command AutoForge. This will now install
all of the dependencies and
automatically start Autoforge. And while
this is installing, if you ever want to
update AutoForge, all you have to do is
run the command npm update- g autoforge
ai. And after setup is complete,
autoforge will open in your browser.
Another way to run this is to simply go
to this GitHub repository. You can then
click on code, download the zip file, or
you can simply get clone from this URL
and then in the downloaded folder, you
will find a file called start
ui.bat
orsh.
Simply run the correct file for your
operating system. And finally, you can
also start AutoForge as a CLI tool. You
don't have to use the UI to do that. You
will have to download the repository.
And in the repository directory, there's
a file called start.bat or start.sh.
That will run autoforge entirely in the
terminal without a UI, but for this
video, we will be using the web app.
Now, I do have to mention that you need
to set up the cloth code CLI. And I
trust that if you're watching this
video, you're already familiar with
setting up Claw Code. If you don't want
to use clawed models, I'll show you
later on in the video how you can use
GLM models instead, which are a lot
cheaper. But for now, I'll simply assume
that you've actually signed in with your
Clawed account. Right, navigating
AutoForge is actually really easy. In
the top nav, you can switch between
light and dark modes, and you also have
access to a couple of themes. I'm
actually going to go with this claw
theme. And if you ever want to view the
documentation, you can simply click on
this button. And now you can learn how
to use the app using the docs. Now let's
start by creating a new project. Then
let's give it a name. These have to be
lowerase and keep up case. We might
change this in the future, but for now
you have to follow this format. I'll
call this project planner. Let's click
on next. And then you have to select a
folder on your machine. This is really
important. Autoforge works with new
projects as well as existing projects.
So for new projects, it's really simple.
I'll simply create a new folder on my
machine like so. And if you're adding
AutoForge to an existing project, simply
select that project folder. Great. Then
let's click on select this folder. And
now we can decide how we want to define
the features of our application. We can
definitely edit the templates manually.
So if we selected this option, AutoForge
will copy a bunch of files over to that
project folder. And you can then use a
text editor to edit the files yourself.
Or we can also use Claude to assist us
with this task. I'll simply select
Claude. Now, this is such a cool
feature. We can now have a conversation
with Claude directly in AutoForge. And
this is where Claude will figure out
what we're trying to build. And finally,
it will give us a list of all the
features that we're going to implement.
Hey there, I'm just trying to build a
very simple project management app. We
could just call this my project
management. And honestly, I don't really
know what features to add. I'm just
trying to create something that will
help me stay on track with all my
deliverables. All right, then let's send
this. You can be as detailed or as vague
as you want. Claude will definitely help
you through that process. So, we get
this response from Claude. And now it's
asking us, do we want to use quick mode
or detailed mode? Now, in quick mode,
Claude will decide on the text stack and
pretty much the entire architecture for
you. But if you're technical and you
want to drive the architecture, then you
can dive into detailed mode. For this
demo, let's just go with quick mode. And
Claude is asking us if we've got any
preferences. So I'll just say you
choose. So I'm just going to kind of
skip ahead by saying, you know what, you
can decide on all the remaining
features. I really just want a super
simple app. Nothing too complicated. But
of course, I do recommend that you spend
a bit of time working with Claude to go
through this entire design. And I also
want to mention that you can attach
files as well. So if you have a design
in mind, you can definitely screenshot
that design and upload it as an image
into this chat. And then let's have a
look. So Claude is giving us basically
all the features. And this is a total of
35 features. I'm just going to say that
sounds good. This app definitely needs
to look polished and it needs to look
very professional. And that's it. So now
C is asking if we're ready to generate
the specification files. So let's just
say yes. Now this step can take a few
minutes. So just be patient. In the
meantime, let's actually have a look at
this target folder. In your project
folder, you will now find this autoforge
subfolder. This contains all the files
needed by the AutoForge app. This also
includes all the prompts like the prompt
for the coding agent and the initializer
agent. And we also have a separate
prompt for the testers. So if you ever
want to change the behavior of the
coding agent or the testing agents, you
can simply open up these files and
adjust the prompt however you want. And
we can see AutoForge just completed all
of these file changes. And if you just
have a look at that in the project, what
it did is it created this app_spec
file. And this file contains everything
related to the project. The project's
name and overview, the tech stack, any
prerequisites, security and access
control, the core features, and more.
So, you might be wondering how this all
works if you're using AutoForge on an
existing project. Well, the good news is
it still works. In this very same
conversation, you can just tell Claude
that, hey, you're starting with an
existing project. So as part of defining
this new feature, you also have to get
familiar with the existing project and
it will then create an appspec file
that's actually based on your existing
project and core features plus the
additional enhancements. The second
change that the agent made was to this
initializer prompt file where it simply
updated the number of features that
should be implemented. Either way, now
that the agent is done, we can simply
click on continue to project or you can
also run YOLO mode. So by default the
agents will try to test their own code.
So as the coding agent is making
changes, it's going to use the playright
MCP server to test the functionality.
Now if you want to skip testing
altogether and just implement features
as quickly as possible, you can simply
run YOLO mode. But I'm actually going to
enable testing. So let's continue to
project. Now the agent might start the
project automatically. If it doesn't
happen for you, you can simply click on
the start button. Now before we click
this, I do want to explain how this app
works. You can set the amount of agents
that should be run concurrently by
dragging this slider. So you can go from
a minimum of one coding agent up to five
parallel agents. Let's just leave it at
three. Then we can also set a schedule.
So if you want autoforge to run during a
certain time of day, we can set up a
schedule as well. Depending on your tech
stack, you can click on this button to
automatically start a development
server. When we click on settings, we
can also enable or disable yolo mode
from here. And then for the playright
MCP server, we can either enable or
disable headless mode. So in headless
mode, the agent won't open up the actual
browser window. It will just kind of do
everything behind the scenes. But if you
disable headless mode, the agent will
actually open up the browser window and
you can see the agent interacting with
the browser itself. Then for the models,
you can select between opus and sonnet.
We do not support haiku at this stage as
it's simply not a good enough coding
model. So by default, we'll just set it
to opus. So over and above your coding
agents, you can also run one to three
regression testing agents. These agents
will pick any features that have already
been implemented and then do regression
testing on those features. So this is
really useful for checking if a recent
change broke some of the existing
functionality. And this regression agent
will then try to repair the fix itself
or if it can't it will change the status
back to failed. And then a future coding
agent will have to pick up that feature
again and repair it. Then you can also
specify how many features should be
processed by a coding agent within a
single session. So if you want a coding
agent to implement one feature at a
time, simply select one. But sometimes
you can push it where you can say, well,
I actually want you to implement two or
three features within a single session.
Now if the coding agent reaches its
context window size, it's going to
compact the conversation and try to
continue with the feature
implementations. So I would say start
off with one feature at a time or maybe
push it to two features in a single
session. Then of course you can change
the theme as well and you can change
between light and dark modes. All right.
So now we can finally start this process
by running the run button. Now if you
want to see exactly what's happening
behind the scenes, what you can do is
click on this debug window. And now you
can see basically this terminal view
which shows exactly what the claude
agent SDK is doing behind the scenes.
And while we're here, let's also discuss
this debug panel. You can press D to
very quickly bring it up. And from here,
you can view the agent's thought
process, which as I mentioned is the
Claude agent SDK's output. If we want,
we can also very quickly spin up the dev
server by effectively pressing this
button up here. Now if you want to start
the dev server yourself or use
terminals, you can definitely do that as
well. So in this terminal window, you
can open up as many terminals as you
want. Right. So the initializer agent is
now busy and this can take a few minutes
to complete. This agent is setting up a
SQLite database with all of the features
for this application. It's also going to
set up your basic framework like if
you're using React or Nex.js, s it will
set up this frameworks for you and
install all the dependencies. And if we
open this autoforge folder, we can now
see this features. DB file and if you
have the SQLite extension installed, you
can see all the features over here. And
for each feature, we can also see this
dependencies array. And in fact, we can
already see this client folder and the
server folder were created by the
initializer agent along with the
components and all the files related to
this project. Now to be clear, the
initializer agent is not going to
implement the entire project. It's just
setting up the fundamentals and
afterwards it will hand all of these
features over to coding agents. So here
we can see that there are 35 features to
implement. We've implemented zero out of 35. We have our pending board with all
of these different tasks. And if we open
up the graph view, we can see all of the
features along with their dependencies.
So this view is basically telling us
that these features do not have any
dependencies on anything else. So these
can be implemented in parallel. And if
we expand mission control and we can see
that maestro the orchestrator agent is
currently waiting for the initializer
agent to complete. And there we go. The
initializer is done. So maestro assigned
these three coding agents. And that is
because we set the concurrency to three
agents up here. And you will also notice
that some of these agents are
implementing more than one feature. So
Octo is only implementing feature five,
but first is working on feature three
and four and Spark is working on feature
one and two. And that is because in the
settings we set the features per agent
to two. Now the reason Octo is only
implementing one feature is because if
we look at the graph, these are the only
five features that can be implemented at
this stage. Everything else has a
dependency on these features. So
therefore, it assigned two features to
the first agent. It assigned two
features to the next one. And then we
only had one feature left to implement.
And if you ever wanted to see exactly
what these coding agents are doing,
there's a couple of ways to do that. You
can simply click on this log button next
to an agent. And here you can see all of
its output streaming in real time. Or if
you just want a highle view, you can
click on recent activity and you can see
all of the output streaming in from
these different agents. So let's have a
look at a few more really cool features.
You can manually add features yourself
by clicking on this plus button. Now you
can give it a name like UI rebrand to
plan forge and let's say please rebrand
the app to plan forge. Now, if you want,
you can provide very detailed steps on
exactly what the agent needs to do. I'm
just going to leave it up to the agent
to decide. And optionally, you can also
provide the priority. By default, this
feature will be added to the bottom of
the feature list, but of course, if you
want, you can definitely assign a higher
priority like one maybe. Then, let's
create this feature. And we can see our
updated feature over here. And well
done, Fizz. F just completed the very
first feature. Now, if you want to add a
whole bunch of features using AI, you
can do that as well. Simply click on
this button, and this will bring up the
Claude chat window again. This time,
Claude will have a look at the existing
project. And now, we can continue having
a conversation. By the end of it, Claude
will create a bunch of new features and
automatically add them to the feature
list. And then here's a feature I really
like. You can click on this chat window.
And in this window, we can have a
conversation with an AI assistant to ask
questions about the codebase. And it can
even add features or give us a status
update as well. Like let's say add a new
feature. The app should support light
and dark modes. Let's send this. So in
this instance, it didn't create a
feature, but it did see that feature 19
is already available and it does cover
this requirement. So this is really
cool. This assistant has access to MCP
tools that it can use to interact with
the features database. Now let's have a
look at using different models with
autoforge. By default, we use the claw
models, so set and opus. But if you
want, we can also use the GLM models or
Olama. So what you have to do is find
your autoforge folder in your user
directory. Then we can open up this env
file in a code editor or text editor.
Now this file contains a lot of
variables that we can override. One
variable I like to use is this N8N
webbook, but we will have a look at this
in a second. What we're looking for are
these overrides. So, we can use Google
Cloud Vertex, we can use GLM, and we can
even use O Lama. So, if we want to use
GLM, all we have to do is uncomment
these variables. So, simply remove these
hashtags at the front of these lines.
Now on the UI, the models will still
show Sonnet, Opus, and Haiku, but we'll
actually swap these out behind the
scenes for the GLM models. All we have
to do is provide our GLM API key. So go
to Z.AI,
go to API, go to API keys, then create a
new API key and add it to this variable.
I am going to do it offscreen, but all
you have to do is paste in your API
token and save this file. Then we need
to stop AutoForge either by pressing
Ctrl C in the terminal or just closing
the terminal window entirely. Then let's
restart AutoForge. You can now see this
GLM badge up here. The same thing
happens if you use O Lama, meaning
you're now using different models. Now
in the settings, this will still show
Opus and Sonnet, but really behind the
scenes, we're swapping this out for the
GLM models. So to test that out, if I
have a look at my current usage, it's
only sitting at 0%. So let's actually
make this like five agents. Let's run
this. And in a minute or two, we should
see this usage increase. And there we
go. We're already using 1%. And of
course, the same thing goes for O Lama.
All you have to do is comment out these
lines. And you do have to download these
models, though, or whatever model you
want. And then you can simply replace
this name with your local model. So for
example, let's say you were using GBTOSS
20B. You can just replace the models
over here. I'll just stick with Gwen 3
coder. Then let's restart AutoForge. And
now we get this OAM logo. Now because
this is running locally, I will rather
just set this back to one agent and
click on start. And now AutoForge will
use a free local model to implement
these features. Now finally I like to
receive notifications to my phone
whenever the agents make progress. To do
that you can simply uncomment this line
from thev file and then you can provide
a web hook to any application. It
doesn't have to be nin by the way. This
web hook will simply send a JSON
structure to any post endpoint which can
then take those values and send WhatsApp
messages, telegram, whatever. I
personally created a very simple N8
workflow that exposes a web hook which
then receives that JSON object and I
then send a notification to myself using
Telegram. So I'm actually going to paste
in that web hook endpoint and I'm going
to save this file. Then just to show you
what those updates look like, it gives
me the name of the actual project and I
can see exactly which features were
implemented by the coding agent as well
as the overall progress. So, please give
this project a spin and let me know down
in the comments what you think. We're
constantly adding new features and
improvements and this is completely
free. You've got nothing to lose. If you
want to become a better AI builder, then
check out Aentic Labs. This is my school
community where like-minded people share
ideas and learn from each other to build
realworld applications using the latest
in AI tech. Thank you for watching. I'll
see you in the next one. Bye-bye.
