#!/usr/bin/env python
#-*- coding: utf8 -*-

from color import Color


class OctreeNode(object):
    """
    Octree Node class para el color quantization
    """

    def __init__(self, level, parent):
        """
       inicar nuevo Octree Node
        """
        self.color = Color(0, 0, 0)
        self.pixel_count = 0
        self.palette_index = 0
        self.children = [None for _ in xrange(8)]
        # add node to current level
        if level < OctreeQuantizer.MAX_DEPTH - 1:
            parent.add_level_node(level, self)

    def is_leaf(self):
        """
        Comprueba que el nodo es una hoja
        """
        return self.pixel_count > 0

    def get_leaf_nodes(self):
        """
       Obtener todos los nodos hoja
        """
        leaf_nodes = []
        for i in xrange(8):
            node = self.children[i]
            if node:
                if node.is_leaf():
                    leaf_nodes.append(node)
                else:
                    leaf_nodes.extend(node.get_leaf_nodes())
        return leaf_nodes

    def get_nodes_pixel_count(self):
        """
        Obtenga una suma del recuento de píxeles para el nodo y sus elementos secundarios
        """
        sum_count = self.pixel_count
        for i in xrange(8):
            node = self.children[i]
            if node:
                sum_count += node.pixel_count
        return sum_count

    def add_color(self, color, level, parent):
        """
        agregar `color` to the tree
        """
        if level >= OctreeQuantizer.MAX_DEPTH:
            self.color.red += color.red
            self.color.green += color.green
            self.color.blue += color.blue
            self.pixel_count += 1
            return
        index = self.get_color_index_for_level(color, level)
        if not self.children[index]:
            self.children[index] = OctreeNode(level, parent)
        self.children[index].add_color(color, level + 1, parent)

    def get_palette_index(self, color, level):
        """
        Obtener índice de paleta para `color`
         Usa `level` para ir un nivel más profundo si el nodo no es una hoja
        """
        if self.is_leaf():
            return self.palette_index
        index = self.get_color_index_for_level(color, level)
        if self.children[index]:
            return self.children[index].get_palette_index(color, level + 1)
        else:
            # get palette index for a first found child node
            for i in xrange(8):
                if self.children[i]:
                    return self.children[i].get_palette_index(color, level + 1)

    def remove_leaves(self):
        """
        agregar todos los píxeles secundarios cuentan y canales de color al nodo principal
         Devuelve el número de hojas extraídas
        """
        result = 0
        for i in xrange(8):
            node = self.children[i]
            if node:
                self.color.red += node.color.red
                self.color.green += node.color.green
                self.color.blue += node.color.blue
                self.pixel_count += node.pixel_count
                result += 1
        return result - 1

    def get_color_index_for_level(self, color, level):
        """
        Obtener índice de `color` para el siguiente` nivel`
        """
        index = 0
        mask = 0x80 >> level
        if color.red & mask:
            index |= 4
        if color.green & mask:
            index |= 2
        if color.blue & mask:
            index |= 1
        return index

    def get_color(self):
        """
        Obtenga un color promedio
        """
        return Color(
            self.color.red / self.pixel_count,
            self.color.green / self.pixel_count,
            self.color.blue / self.pixel_count)


class OctreeQuantizer(object):
    """
    Clase Octree Quantizer para cuantificación de color de imagen
     Utilice MAX_DEPTH para limitar una cantidad de niveles
    """

    MAX_DEPTH = 8

    def __init__(self):
        """
       iniciar Octree Quantizer
        """
        self.levels = {i: [] for i in xrange(OctreeQuantizer.MAX_DEPTH)}
        self.root = OctreeNode(0, self)

    def get_leaves(self):
        """
        Obtener todas las hojas
        """
        return [node for node in self.root.get_leaf_nodes()]

    def add_level_node(self, level, node):
        """
        agregar `nodo` a los nodos del` nivel`
        """
        self.levels[level].append(node)

    def add_color(self, color):
        """
        agregar `color` al  Octree
        """
        # passes self value as `parent` to save nodes to levels dict
        self.root.add_color(color, 0, self)

    def make_palette(self, color_count):
        """
        Hacer una paleta de colores con el máximo de colores `color_count`
        """
        palette = []
        palette_index = 0
        leaf_count = len(self.get_leaves())
        # reduce nodes
        # up to 8 leaves can be reduced here and the palette will have
        # only 248 colors (in worst case) instead of expected 256 colors
        for level in xrange(OctreeQuantizer.MAX_DEPTH - 1, -1, -1):
            if self.levels[level]:
                for node in self.levels[level]:
                    leaf_count -= node.remove_leaves()
                    if leaf_count <= color_count:
                        break
                if leaf_count <= color_count:
                    break
                self.levels[level] = []
        # build palette
        for node in self.get_leaves():
            if palette_index >= color_count:
                break
            if node.is_leaf():
                palette.append(node.get_color())
            node.palette_index = palette_index
            palette_index += 1
        return palette

    def get_palette_index(self, color):
        """
        Obtener índice de paleta para `color`
        """
        return self.root.get_palette_index(color, 0)
