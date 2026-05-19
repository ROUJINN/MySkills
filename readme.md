usage:

查找 ~/.codex/skills/ 下的所有软链接（-type l）并删除，然后重新链接
find ~/.codex/skills/ -type l -delete
ln -snf ~/Desktop/code/MySkills/* ~/.codex/skills/

created by myself:

add-reference
summarize-reference

adapted from https://github.com/Orchestra-Research/AI-research-SKILLs :

academic-plotting
brainstorming-research-ideas
creative-thinking-for-research
ml-paper-writing
presenting-conference-talks

测试：
add-reference https://arxiv.org/abs/1601.00991
add-reference 
