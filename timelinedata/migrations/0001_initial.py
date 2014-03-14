# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Timeline'
        db.create_table(u'timelinedata_timeline', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('highlighted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('orig_titles', self.gf('django.db.models.fields.CharField')(default='', max_length=2000, blank=True)),
            ('events', self.gf('django.db.models.fields.CharField')(max_length=1000000, blank=True)),
            ('banned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fewer_than_threshold', self.gf('django.db.models.fields.BooleanField')()),
            ('first_and_last', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('errors', self.gf('django.db.models.fields.CharField')(max_length=1000000, blank=True)),
            ('single_section', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('extra_ignore_sections', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('separate', self.gf('django.db.models.fields.BooleanField')()),
            ('continuations', self.gf('django.db.models.fields.BooleanField')()),
            ('keep_row_together', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'timelinedata', ['Timeline'])


    def backwards(self, orm):
        # Deleting model 'Timeline'
        db.delete_table(u'timelinedata_timeline')


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
            'highlighted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keep_row_together': ('django.db.models.fields.BooleanField', [], {}),
            'orig_titles': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            'separate': ('django.db.models.fields.BooleanField', [], {}),
            'single_section': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['timelinedata']