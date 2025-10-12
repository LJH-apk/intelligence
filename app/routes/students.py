# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：students.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/9 18:33 
@PyVersion ：3.10 arm64
'''
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from app import db
from app.models import Student

bp = Blueprint('student', __name__)
@bp.route('/')
def student_list():
    students = Student.query.all()
    return render_template('students/list.html',students=students)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        new_student = Student(name=name,age=age)
        db.session.add(new_student)
        db.session.commit()

        flash("学生创建成功","success")
        return "创建成功"

@bp.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('删除学生成功','success')
    return jsonify({
            "code": 200,
            "status": "success",
            "message":{
                "name":student.name,
                "info":"ok"
            }
        })

@bp.route('/edit/<int:id>')
def edit_student(id):
    student = Student.query.get_or_404(id)
    student.name = request.form['name']
    student.age = request.form['age']
    db.session.commit()
    return jsonify({
        "code": 200,
        "status": "success",
        "message":{
            "name":student.name,
            "info":"updated"
        }
    })


@bp.route('/init')
def init():
    name = "name"
    age = "age"
    created_at = datetime(2025, 10, 9, 19, 5, 0)
    updated_at = datetime(2025, 10, 9, 19, 5, 0)

    new_people = Student(name=name, age=age, created_at=created_at, updated_at=updated_at)
    db.session.add(new_people)
    db.session.commit()

    return "初始化完成"