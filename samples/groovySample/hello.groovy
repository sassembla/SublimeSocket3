// sample hello world

class Greet {
	def name

	Greest(who) {
		name = who[0].toUpperCase() + who[1..-1]
	}

	def salute() {
		println "Hello $name!"
	}

}

g = new Greet('world')
g.salute()