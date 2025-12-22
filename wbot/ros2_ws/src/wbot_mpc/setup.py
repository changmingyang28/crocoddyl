from setuptools import find_packages, setup

package_name = 'wbot_mpc'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/mpc_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='guanyu',
    maintainer_email='guanyu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mpc_node = wbot_mpc.mpc_node:main',
        ],
    },
)
