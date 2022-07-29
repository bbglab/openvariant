.. _Contribution guide:

*********************
Contribution guide
*********************

This is a brief guidelines that you need to know in order to make a contribution to the project.

#. `Fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ the repository (don't try to commit on the **OpenVariant** main repository).
#. Clone your fork to your local (your computer). If you have the repo already cloned from the main GitHub repository, just
   add a new remote pointing at your fork, like this: ``git remote add fork <cloning address of your fork>``. Check if it
   looks good: ``git remote -v``.

   *Note: you can call this remote pointing to your fork as fork or upstream (more correct way of calling it).*

#. Create a new branch, like this: ``git checkout -b my_new_shiny_feature`` (the name of the new branch should be related
   to with the issue or feature that wants to be implemented).
#. Code, make the required changes or add your new fancy feature.
#. Add changes: ``git add -p``
#. Commit them: ``git commit -m "feat: added a nice feature"``
#. Push it to your remote fork: ``git push origin my_new_shiny_feature``
#. Go to your fork on GitHub where your branch is. Find the option "`Pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests>`_"
   which will open a pull request with the changes and make sure you are comparing your ``develop``-derived branch in your
   fork to the ``develop`` branch from the ``openvariant`` repo:


*Note: You can add both your fork and main repo to your local git repo as remote. Check what you have in remote:* ``git remote -v`` *.
If you cloned from your fork, then it should point there. You can add the main repo with git remote add*

Commit messages
===============================================

For a good practise, it is recommended to follow `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_
guidance with short and self-explanatory commits.