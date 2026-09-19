"""Writing the corpus out as the files the PHP server loads.

The mirror image of ``importing``: that package reads what the linguists send
and checks it, this one hands the checked result on.  Nothing here validates
anything, because by the time a row is in the database it has already passed
every check ``importing`` makes.
"""
