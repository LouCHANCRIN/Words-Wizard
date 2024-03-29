from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import csv
import datetime

from ..schemas import PostBase, PostResponse, CreateWordsResponse, WordResponse
from .. import models, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/words",
    tags=["Words"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)

@router.post('/', status_code=201, response_model=PostResponse)
def insert_word(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.get('/get_flashcards', status_code=200, response_model=List[WordResponse])
def get_flashcards(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    words_data = db.query(models.Word).where(models.Word.meaning != "").order_by(func.random()).limit(9).all()
    words_list = [word.__dict__ for word in words_data]

    if not words_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No word found in database'
        )

    for word in words_list:
        word.update({"show_translation": False})
    return words_list

@router.get('/get_words', status_code=200, response_model=List[WordResponse])
def get_word(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    words_data = db.query(models.Word).order_by(func.random()).limit(9).all()
    words_list = [word.__dict__ for word in words_data]

    if not words_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No word found in database'
        )
    return words_list

@router.get('/check_words', status_code=201, response_model=CreateWordsResponse)
def check_words(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print("Uploading words to database")
    with open("./data/Chinese All Characters (Merged).csv", 'r') as file:
        csvreader = csv.reader(file)
        count = 0
        words = []
        for row in csvreader:
            if count > 0:
                row[2] = row[2].replace(" ", ",").replace(" ", ",")
                words.append(models.Word(
                    radical = row[2],
                    frequency = int(row[3]) if row[3] != "" else 0,
                    general_standard = int(row[4]) if row[4] != "" else 0,
                    encounters = int(row[5]) if row[5] != "" else 0,
                    fraction_of_the_language = float(row[6].replace("%", "").replace(",", ".")),
                    hsk1 = row[7],
                    hsk2 = row[8],
                    stroke_count = int(row[9]) if row[9] != "" else 0,
                    character = row[10],
                    pinyin = row[11],
                    pinyin2 = row[12],
                    tone = row[13],
                    meaning = row[14],
                ))
            count += 1

    for word in words:
        db.add(word)
        db.commit()
        db.refresh(word)

    return {"words_inserted": count - 1}
