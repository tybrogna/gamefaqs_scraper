

class Save_Name:
    def __init__(self, name):
        self.name = name


class Main_Step(Save_Name):
    def __init__(self, name, run_func, save_loc="", completion=False):
        super().__init__(name)
        self.save_loc = save_loc
        self.run_func = run_func
        self.completion = completion

    def __eq__(self, other):
        if not isinstance(other, Main_Step):
            return NotImplemented
        return self.name == other.name and self.save_loc == other.save_loc  # and self.completion == other.completion

    def __str__(self):
        return "Main Step {0} \n    {1}, {2}, {3}" \
            .format(
                self.name,
                self.run_func,
                self.save_loc if self.save_loc != "" else "No Save Location",
                "Finished" if self.completion else "Incomplete")


class File_Step(Save_Name):
    def __init__(self, name, link, save_loc, completion):
        super().__init__(name)
        self.save_loc = save_loc
        self.link = link
        self.completion = completion

    def __eq__(self, other):
        if not isinstance(other, File_Step):
            return NotImplemented
        return self.name == other.name and \
            self.save_loc == other.save_loc \
            and self.link == other.link  # and self.completion == other.completion

    def __str__(self):
        return "File Step {0} \n    {1},\n    {2},\n    {3}" \
            .format(self.name, self.save_loc, self.link, "Finished" if self.completion else "Incomplete")


class Link_Step(Save_Name):
    def __init__(self, name, link, completion):
        super().__init__(name)
        self.link = link
        self.completion = completion

    def __eq__(self, other):
        if not isinstance(other, Link_Step):
            return NotImplemented
        return self.name == other.name and self.link == other.link  # and self.completion == other.completion

    def __str__(self):
        return "Link Step {0} \n    {1}, {2}" \
            .format(self.name, self.link, "Finished" if self.completion else "Incomplete")
