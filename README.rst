cron_install
#############

A simple command to install a cron table, and make it evolve over time.

.. figure:: cron_install-logo.svg

Use it in a deployement task to deploy a file containing your crontab.

Usage
=====

Call the command using the module name.

Indicate a marker, unique on the host,
with `-m` option,
that will help identify the start / end of your specific tasks in crontab.

Indicate a file containing your crontab.
The file may reference environment variables,
that will be replaced at installation time using the `python builtin template module`_.

For example, if we have a file `crontab.tpl` containing::

  MAILTO="$ADMIN_MAIL"
  # recompute the model
  0 0 * * * python -m project.rebuild_model >>/dev/null
  # check stuff in $STUFF_DIRNAME
  */10 * * * /usr/local/bin/check_stuff $STUFF_DIRNAME >>/dev/null

Launching::

  $ ADMIN_MAIL="admin@acme.info" STUFF_DIRNAME="/srv/stuff" python3 -m cron_install -m MY_PROJECT crontab.tpl

Will install the following table::

  $ crontab -l
  # START MY_PROJECT
  MAILTO="admin@acme.info"
  # recompute the model
  0 0 * * * python -m project.rebuild_model >>/dev/null
  # check stuff in /srv/stuff
  */10 * * * /usr/local/bin/check_stuff /srv/stuff >>/dev/null
  # END MY_PROJECT

On a new run,
all the part between `# START MY_PROJECT` and `# END MY_PROJECT`,
will be replaced by the new crontab.

.. _`python builtin template module`: https://docs.python.org/3.7/library/string.html#template-strings