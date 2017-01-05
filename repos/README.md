Working copies of all the code repos that get packaged into the container. Allows off-line modification rather than checking them out directly during the container build process.

### *Laissez faire* steps

1. Initial step: `./checkout_all.sh`
2. If there are any changes on GH you want to grab: `./pull_all.sh`

### Visible hand option

Modify whatever you want, how you want. Rebuild image as per root `Dockerfile`.
