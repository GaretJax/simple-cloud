from simplecloud import images


add = images.Manager.make_add_command('imgadd')
ls = images.Manager.make_list_command('images')
rm = images.Manager.make_remove_command('imgrm')
