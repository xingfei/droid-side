droid-side
==========

droid-side is a tools suite to help the development of android projects.

so far, there is only one tool in the suite.

Tool: android_object.py
=====
Use it to generate java objects that can be used in android project. 
These objects can be created from JSONObject, or transferred from activity to activity.

Every object has a constructor with a JSONObject parameter, and values can be extracted from the JSONObject. And every object implements the android.os.Parcelable interface, thus their instances can be put in the bundle and transferred from activity to activity.

how to use it
====

 - write a text file to define your objects with their name and fields(field type & name). syntax is very simple, you can get familiar with it in less than 10 minutes.
 - use android_object.py script to generate objects

object definition file syntax
===
@see example/objects.txt for example.
 - define the objects' package, using a #package com.example.subfolder line
 - start define an object, using a @object_name line
 - start define object field, lines after @object_name line are the field of the object, until reached another @object directive or the end of the file.
 - field start with a type, allowed types are boolean, int, double, long, String or other object.
 - field name(s) are after the type. you can define any number of field of the same type in one line.

script usage
===
The script is a common python file. Execute it as normal python scripts, along with two arguments.
 - object-definition-file: the path of the object definition file
 - target-directory: the directory of the generated file, the top folder of the java source file. often the src folder of the android projects.

command is: /path/to/android_object.py /path/to/objects.txt /path/to/target/directory

On windows, associate *.py to python.exe, on linux/unix, use python to execute the script, or make the script executable using chmod command.
In either case, the command is similar.
