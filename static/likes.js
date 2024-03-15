"use strict";

const $likeBtn = $('.like-button');
const CHECK_LIKE_URL = "/api/likes";
const ADD_LIKE_URL = "/api/like";
const UNLIKE_URL = "/api/unlike";

/** handles the clikc of the like button. Makes request to like api to check if liked */
async function handleLikeClick() {

  const cafeId = $likeBtn.attr('id');
  console.log(cafeId)

  const liked = await isLiked(cafeId);
  console.log(liked)

  if (liked) {
    await unlikeCafe(cafeId);
    changeButtonToUnliked();
  } else {
    await likeCafe(cafeId);
    changeButtonToLiked();
  }
}

/** makes a request to lunike API to unnlike a cafe */
async function unlikeCafe(cafe_id) {
  const respnse = await fetch(
    UNLIKE_URL,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        "cafe_id": Number(cafe_id)
      })
    }
  );
}

/** makes a request to like API to add a cafe to user likes */
async function likeCafe(cafe_id) {
  const respnse = await fetch(
    ADD_LIKE_URL,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        "cafe_id": Number(cafe_id)
      })
    }
  );
}

/** checks like status of a cafe */
async function isLiked(cafeId) {
  const params = new URLSearchParams({ cafe_id: cafeId });

  const resp = await fetch(`${CHECK_LIKE_URL}?${params}`);
  const data = await resp.json();

  return data.likes === true;
}

/** change to a liked button */
function changeButtonToLiked() {
  $likeBtn.html("Unlike")
    .removeClass("btn-outline-primary")
    .addClass("btn-primary");
}

/** change to a unliked button */
function changeButtonToUnliked() {
  $likeBtn.html("Like")
    .removeClass("btn-primary")
    .addClass("btn-outline-primary");
}


$likeBtn.on('click', handleLikeClick);

async function start() {
  const cafeId = $likeBtn.attr('id');
  const liked = await isLiked(cafeId);

  if (liked) {
    changeButtonToLiked();
  } else {
    changeButtonToUnliked();
  }
}

start();