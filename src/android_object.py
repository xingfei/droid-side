#!/usr/bin/env python

import os

def java_type_name(type_name):
    t = type_name.split('_')
    return ''.join([s.title() for s in t])

def java_field_name(field_name):
    t = field_name.split('_')
    if len(t) == 1:
        return field_name
    else:
        return t[0] + ''.join([s.title() for s in t[1:]])

def is_primative(t):
    return t in ['boolean', 'double', 'int', 'long', 'String']

class Field:
    def __init__(self, f_type, f_name, is_array):
        self.is_array = is_array
        self.data = {
            'f_type': f_type, 'f_name': java_field_name(f_name),
            'f_type_title': f_type.title(),
            'k_name': f_name
        }

    def definition(self):
        if self.is_array:
            return 'public %(f_type)s[] %(f_name)s;' % self.data
        else:
            return 'public %(f_type)s %(f_name)s;' % self.data

class PrimativeField(Field):
    def read_from_json(self):
        if self.is_array:
            return '''
        if (data.has("%(k_name)s")) {
            org.json.JSONArray arr = data.getJSONArray("%(k_name)s");
            int len = arr.length();
            %(f_name)s = new %(f_type)s[len];
            for (int i = 0 ; i < len ; i++) {
                %(f_name)s[i] = arr.get%(f_type_title)s(i);
            }
        }''' % self.data
        else:
            return '%(f_name)s = data.opt%(f_type_title)s("%(k_name)s");' % self.data

    def read_from_parcel(self):
        if self.is_array:
            return '%(f_name)s = in.create%(f_type_title)sArray();' % self.data
        else:
            return '%(f_name)s = in.read%(f_type_title)s();' % self.data

    def write_to_parcel(self):
        if self.is_array:
            return 'dest.write%(f_type_title)sArray(%(f_name)s);' % self.data
        else:
            return 'dest.write%(f_type_title)s(%(f_name)s);' % self.data
class BooleanField(PrimativeField):
    def read_from_parcel(self):
        if self.is_array:
            return '''
        int[] _%(f_name)s = in.createIntArray();
        if (_%(f_name)s != null) {
            %(f_name)s = new boolean[_%(f_name)s.length];
            for (int i = 0 ; i < _%(f_name)s.length ; i++) {
                %(f_name)s[i] = (_%(f_name)s[i] != 0);
            }
        }''' % self.data
        else:
            return '%(f_name)s = (in.readInt() != 0);' % self.data

    def write_to_parcel(self):
        if self.is_array:
            return '''
        if (%(f_name)s == null){
            dest.writeIntArray((int[])null);
        } else {
            int[] _%(f_name)s = new int[%(f_name)s.length];
            for (int i = 0 ; i < %(f_name)s.length ; i++) {
                _%(f_name)s[i] = (%(f_name)s[i] ? 1 : 0);
            }
            dest.writeIntArray(_%(f_name)s);
        }''' % self.data
        else:
            return 'dest.writeInt(%(f_name)s ? 1 : 0);' % self.data

class ObjectField(Field):

    def read_from_json(self):
        if self.is_array:
            return '%(f_name)s = data.has("%(k_name)s") ? %(f_type)s.loadArray(data.getJSONArray("%(k_name)s")) : null;' % self.data
        else:
            return '%(f_name)s = data.has("%(k_name)s") ? new %(f_type)s(data.getJSONObject("%(k_name)s")) : null;' % self.data

    def read_from_parcel(self):
        if self.is_array:
            return '%(f_name)s = (%(f_type)s[])in.readParcelableArray(null);' % self.data
        else:
            return '%(f_name)s = (%(f_type)s)in.readParcelable(null);' % self.data

    def write_to_parcel(self):
        if self.is_array:
            return 'dest.writeParcelableArray(%(f_name)s, flags);' % self.data
        else:
            return 'dest.writeParcelable(%(f_name)s, flags);' % self.data

class VO:
    def __init__(self, name):
        self.name = name
        self.fields = []

    def add_field(self, f):
        self.fields.append(f)

    def gen_file(self, directory, package, parent_class, meta):
        type_name = java_type_name(self.name)
        file_path = os.path.join(directory, type_name + '.java')

        _data = {'type_name': type_name}

        out = open(file_path, 'w')

        print >> out, '''
package %s;

import android.os.Parcel;
import android.os.Parcelable;

'''% package

        # write class name
        if parent_class:
            print >> out, 'public class %s extends %s implements Parcelable {' % (type_name, parent_class)
        else:
            print >> out, 'public class %s implements Parcelable {' % type_name

        # write fields definitions
        for field in self.fields:
            print >> out, '    %s' % field.definition()
        
        # default constructor
        print >> out, '    public %s() {}' % type_name

        # construct from json
        print >> out, '    public %s(org.json.JSONObject data) throws org.json.JSONException {' % type_name
        for field in self.fields:
            print >> out, '        %s' % field.read_from_json()
        print >> out, '    }'

        # construct from Parcel
        print >> out, '    private %s(Parcel in) {' % type_name
        for field in self.fields:
            print >> out, '        %s' % field.read_from_parcel()
        print >> out, '    }'

        # write to Parcel
        print >> out, '    public void writeToParcel(Parcel dest, int flags) {'
        for field in self.fields:
            print >> out, '        %s' % field.write_to_parcel()
        print >> out, '    }'

        # 1. load array from json array
        # 2. Parcelable implementation
        print >> out, '''
    public static %(type_name)s[] loadArray(org.json.JSONArray array) throws org.json.JSONException {
        int len = array.length();
        %(type_name)s[] result = new %(type_name)s[len];
        if (len > 0) {
            for (int i = 0; i < len; i++) {
                org.json.JSONObject o = array.getJSONObject(i);
                result[i] = new %(type_name)s(o);
            }
        }
        return result;

    }

    public int describeContents() {
        return getClass().getName().hashCode();
    }

    public static final Parcelable.Creator<%(type_name)s> CREATOR = new Parcelable.Creator<%(type_name)s>() {
        public %(type_name)s createFromParcel(Parcel in) {
            return new %(type_name)s(in);
        }

        public %(type_name)s[] newArray(int size) {
            return new %(type_name)s[size];
        }
    };''' % _data


        print >> out, '} // end class'

        out.close()

class AndroidObjects:
    def __init__(self):
        self.meta = {}
        self.package = ''
        self.parent_class = ''
        self.objects = []

    def parse(self, lines):
        for line in lines:
            self._parse(line.strip())

        if self.package == '':
            raise Exception('you must specify package')

        if len(self.objects) == 0:
            raise Exception('no objects found')

    def _parse(self, line):
        if not line: return

        c = line[0]
        if c == '#':
            t = line[1:].split()
            if hasattr(self, t[0]):
                setattr(self, t[0], t[1])
            else:
                self.meta[t[0]] = t[1]
        elif c == '@':
            vo = VO(line[1:])
            self.objects.append(vo)
        else:
            vo = self.objects[-1]
            t = line.split()
            f_type = t[0]
            if f_type.endswith('[]'):
                is_array = True
                f_type = f_type[:-2]
            else:
                is_array = False

            if f_type in ['double', 'int', 'long', 'String']:
                clz = PrimativeField
            elif f_type == 'boolean':
                clz = BooleanField
            else:
                clz = ObjectField
                f_type = f_type.title()

            for f_name in t[1:]:
                vo.add_field(clz(f_type, f_name, is_array))

    def gen_files(self, directory):
        if not os.path.exists(directory):
            raise Exception('directory not found')

        file_directory = os.path.join(directory, self.package.replace('.', os.path.sep))
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        for vo in self.objects:
            vo.gen_file(file_directory, self.package, self.parent_class, self.meta)


if __name__ == '__main__':
    import sys
    objects_file = sys.argv[1]
    target_directory = sys.argv[2]

    ao = AndroidObjects()
    lines = open(objects_file)
    ao.parse(lines)
    lines.close()

    ao.gen_files(target_directory)
