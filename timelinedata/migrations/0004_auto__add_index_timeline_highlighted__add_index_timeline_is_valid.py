# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Timeline', fields ['highlighted']
        db.create_index(u'timelinedata_timeline', ['highlighted'])

        # Adding index on 'Timeline', fields ['is_valid']
        db.create_index(u'timelinedata_timeline', ['is_valid'])


    def backwards(self, orm):
        # Removing index on 'Timeline', fields ['is_valid']
        db.delete_index(u'timelinedata_timeline', ['is_valid'])

        # Removing index on 'Timeline', fields ['highlighted']
        db.delete_index(u'timelinedata_timeline', ['highlighted'])


    models = {
        u'timelinedata.timeline': {
            'Meta': {'object_name': 'Timeline'},
            'banned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'continuations': ('django.db.models.fields.BooleanField', [], {}),
            'errors': ('django.db.models.fields.CharField', [], {'max_length': '1000000', 'blank': 'True'}),
            'events': ('django.db.models.fields.CharField', [], {'max_length': '1000000', 'blank': 'True'}),
            'extra_ignore_sections': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'fewer_than_threshold': ('django.db.models.fields.BooleanField', [], {}),
            'first_and_last': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'highlighted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'keep_row_together': ('django.db.models.fields.BooleanField', [], {}),
            'orig_titles': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            'separate': ('django.db.models.fields.BooleanField', [], {}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'single_section': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'sort_order_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['timelinedata']