# -*- coding: utf-8 -*-
import logging
import os

from morghulis.os_utils import ensure_dir

log = logging.getLogger(__name__)


class DarknetExporter:

    def __init__(self, wf):
        self.widerface = wf

    @staticmethod
    def _convert(img_size, box):
        dw = 1. / img_size[0]
        dh = 1. / img_size[1]
        cx, cy = box.center
        x = cx * dw
        w = box.w * dw
        y = cy * dh
        h = box.h * dh
        return max(0.005, x), max(0.005, y), min(0.995, w), min(0.995, h)

    def _export(self, target_dir, dataset_name='train'):
        log.info('Converting %s data', dataset_name)
        images_root = os.path.join(target_dir, 'images/')
        annotations_root = os.path.join(target_dir, 'labels/')
        ensure_dir(annotations_root)
        with open(os.path.join(target_dir, '{}.txt'.format(dataset_name)), 'w') as f:
            for i in self.widerface.images():
                if len(i.faces) > 0:
                    path = i.copy_to(images_root, include_subdirs=True)
                    f.write('{}\n'.format(path))
                    head, _ = os.path.splitext(path)
                    head, tail = os.path.split(head)
                    annotation_dir = os.path.join(annotations_root, i.subdir)
                    ensure_dir(annotation_dir)
                    annotation_file = os.path.join(annotation_dir, tail+'.txt')
                    with open(annotation_file, 'w') as anno:
                        for face in i.faces:
                            bbox = self._convert(i.size, face)
                            anno.write('0 ' + ' '.join([str(a) for a in bbox]) + '\n')

    @staticmethod
    def _prepare(target_dir):
        log.info('Preparing target dir: %s', target_dir)
        ensure_dir(os.path.join(target_dir, 'images/'))
        ensure_dir(os.path.join(target_dir, 'labels/'))
        ensure_dir(os.path.join(target_dir, 'backup/'))

        log.info('Creating obj.names')
        with open(os.path.join(target_dir, 'obj.names'), 'w') as obj_names:
            obj_names.write('face\n')

        log.info('Creating obj.data')
        with open(os.path.join(target_dir, 'obj.data'), 'w') as obj_data:
            obj_data.write('classes = 1\n')
            obj_data.write('train = train.txt\n')
            obj_data.write('valid = val.txt\n')
            obj_data.write('names = obj.names\n')
            obj_data.write('backup = backup/\n')

    def export(self, target_dir):
        ensure_dir(target_dir)
        self._prepare(target_dir)
        self._export(target_dir)
