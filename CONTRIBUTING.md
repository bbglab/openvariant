# Contribution guide

This is a brief guidelines that you need to know in order to make a contribution to the project.

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the repository (don't try to commit on the **OpenVariant** main repository).
2. Clone your fork to your local (your computer). If you have the repo already cloned from the main GitHub repository, just
   add a new remote pointing at your fork, like this: ``git remote add fork <cloning address of your fork>``. Check if it
   looks good: ``git remote -v``.

   *Note: you can call this remote pointing to your fork as fork or upstream (more correct way of calling it).*

3. Create a new branch, like this: ``git checkout -b my_new_shiny_feature`` (the nam of the new branch should be related
   with the issue or feature that wants to be implemented).
4. Code, make the required changes or add your new fancy feature.
5. Add changes: ``git add -p``
6. Commit them: ``git commit -m "feat: added a nice feature"``
8. Push it to your remote fork: ``git push origin my_new_shiny_feature``
9. Go to your fork on GitHub where your branch is. Find the option "[Pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)"
   which will open a pull request with the changes and make sure you are comparing your ``develop``-derived branch in your
   fork to the ``develop`` branch from the ``openvariant`` repo:


*Note: You can add both your fork and main repo to your local git repo as remote. Check what you have in remote:* ``git remote -v`` *.
If you cloned from your fork, then it should point there. You can add the main repo with git remote add*

### Commit messages

For a good practice, it is recommended to follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
guidance with short and self-explanatory commits.

## Development — Rust toolchain

To set up the Rust environment for the latest release, ensure you have `rustup` installed. You can install it or update to the latest stable version with:

```bash
rustup update stable
```

### Compiling OpenVariant Rust version

To compile the Rust core of OpenVariant, you can use `uv` to manage the Python interpreter during the build process:

```bash
uv sync
uv run maturin develop
```

This command automatically locates the appropriate Python interpreter and builds the Rust components in `debug` mode. The resulting shared library will be located in `target/debug/`.