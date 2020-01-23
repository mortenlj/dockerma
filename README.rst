DockerMA - Docker Multi Architecture
====================================

DockerMA facilitates building multi-arch containers with minimal fuss.

What does it do?
----------------

``dockerma`` aims to be a drop-in replacement for ``docker build`` and ``docker push`` to handle building what is often
referred to as "multi-arch" images. A "multi-arch" image is actually a manifest, listing which actual image to use for
a given architecture. The way to create these are still somewhat cumbersome, and considered experimental, especially if
you are using a base image that is already "multi-arch".

``dockerma build`` works by reading your ``Dockerfile`` and looking for a specially formatted comment that selects which
architectures you want to build. It will then create a manipulated version of your ``Dockerfile``, to inject some tools
for cross-building, and then build architecture specific images. If you have selected ``amd64`` and ``arm``, and build
``myapp:v1.0``, the build will produce ``myapp:v1.0-amd64`` and ``myapp:v1.0-arm``.

``dockerma push`` will take the architecture specific images that was built previously, and push them to the remote
registry. It will then create a manifest, listing each of the images for the wanted architectures, and push the manifest
under the requested tag. This will create a "multi-arch" image.

Supported architectures is based on what is available in the tooling used. The cross-building tools are from
https://github.com/monsonnl/qemu-wrap-build-files, and at this writing only supports ``amd64``, ``arm`` and ``arm64``.
If you want ``dockerma`` to support other architectures, you need to persuade ``qemu-wrap-build-files`` to support it
first.

How do I use it?
----------------

Since ``dockerma`` aims to be a drop-in replacement, using it should be fairly simple.

The first step is to add the ``dockerma`` comment to your ``Dockerfile``::

    # dockerma archs:arm,amd64,arm64:


When you previously used ``docker build -t myapp:latest -t myapp:v1.0 .`` to build ``latest`` and ``v1.0`` tags for your
current architecture, you will now simply replace ``docker`` with ``dockerma``::

    dockerma build -t myapp:latest -t myapp:v1.0 .


Similary, where you used ``docker push -t myapp:latest``, you now use ``dockerma``::

    dockerma push myapp:latest

What are the requirements?
--------------------------

* You need to enable experimental features in ``docker``. This can be done by setting ``DOCKER_CLI_EXPERIMENTAL`` to
  ``enabled``, or changing your docker configuration. Consult the docker documentation for details.
* Your build host must support running ``qemu-<arch>-static``.
* Your base images needs to already support multi-arch (and in particular, the architectures you want to support).
  Many official images already do.

Are there any downsides to this approach?
-----------------------------------------

* All images will have some additional files from the cross-build tooling, located in ``/cross-build``.

Releasing a new version
-----------------------

1. Tag the new version: ``git tag -a v1.2.3``
2. Push the tag to Github: ``git push origin v1.2.3``
3. The new version is published to PyPI and Github
