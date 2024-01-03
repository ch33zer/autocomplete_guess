const DomProxy = new Proxy(Object.freeze({}), {
  get: function(target, prop, receiver) {
    return document.getElementById(prop)
  }
})
class State {
	constructor(prompt, answers) {
		this.prompt = prompt
		this.answers = answers
		this.already_guessed = []
		this.original_answers = [...answers]
		this.chances = 3
	}
	valid(guessed) {
		if (this.chances <= 0) {
			return false
		}
		for (const already of this.already_guessed) {
			if (already === guessed) {
				return false
			}
		}
		return true
	}
	check(guessed) {
		this.already_guessed.push(guessed)
		for (let i = 0; i < this.answers.length; i++) {
			const answer = this.answers[i]
			if (answer === guessed) {
				this.answers.splice(i, 1)
				return true
			}
		}
		this.chances -= 1
		return false
	}
	won() {
		return this.answers.length == 0
	}
	lost() {
		return this.chances <= 0 && !this.won()
	}
}
let STATE = null;
function reset() {
	DomProxy.attempts_cnt.value = STATE.chances
	DomProxy.completions_cnt.value = STATE.answers.length
	DomProxy.guess_list.innerHTML = ''
	DomProxy.answer_input.value = ''
	DomProxy.solution_list.innerHTML = ''
	DomProxy.solution_status.innerHTML = ''
	DomProxy.solution_status.classList.remove("win")
	DomProxy.solution_status.classList.remove("lose")
	DomProxy.solution.hidden = true
}
function show_results(won) {
	let msg = "You won! You guessed all the completions."
	let cls = "win"
	if (!won) {
		msg = `You didn't guess the right completions! You got ${STATE.original_answers.length - STATE.answers.length} of ${STATE.original_answers.length} answers correct.`
		cls = "lose"
	}
	DomProxy.solution_status.innerText = msg
	DomProxy.solution_status.classList.add(cls)
	for (const ans of STATE.original_answers) {
		const li = document.createElement("li");
		const text = document.createTextNode(ans);
		li.appendChild(text)
		DomProxy.solution_list.appendChild(li)
	}
	DomProxy.solution.hidden = false
}
function win() {
	show_results(true)
}
function lose() {
	show_results(false)
}
async function get_completions(prompt) {
	return ["foo"]
	const r = await fetch("get_completions/" + prompt)
	const json = await r.json()
	console.log(json)
	return json
}
function record_guess(guess, correct) {
	const li = document.createElement("li");
	const guessText = document.createTextNode((correct ? "✅" : "❌") + " " + guess);
	li.appendChild(guessText)
	DomProxy.guess_list.appendChild(li)
}
function submit_answer() {
	const answer = DomProxy.answer_input.value.toLowerCase().trim()
	if (answer.length == 0) {
		return
	}
	if (!STATE.valid(answer)) {
		return
	}
	const correct = STATE.check(answer)
	record_guess(answer, correct)
	DomProxy.attempts_cnt.value = STATE.chances
	DomProxy.completions_cnt.value = STATE.answers.length
	if (STATE.won()) {
		win();
	}
	else if (STATE.lost()) {
		lose();
	}
}
async function play() {
	const prompt = DomProxy.prompt_input.value.toLowerCase().trim()
	if (prompt.length == 0) {
		return
	}

	completions = await get_completions(prompt)

	STATE = new State(prompt, completions)
	reset()
	DomProxy.game.hidden = false
}
function onload() {
	DomProxy.submit_prompt.addEventListener("click", play)
	DomProxy.answer_submit.addEventListener("click", submit_answer)
	DomProxy.prompt_input.addEventListener("keypress", (e) => {
		if (e.key === "Enter") {
			DomProxy.submit_prompt.click()
		}
	})
	DomProxy.answer_input.addEventListener("keypress", (e) => {
		if (e.key === "Enter") {
			DomProxy.answer_submit.click()
		}
	})
}
window.addEventListener("load", onload)
