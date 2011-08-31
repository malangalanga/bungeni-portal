
#### COMMMON FUNCTIONS ####

=begin
Prompt the user to enter the value for a variable
=end
def prompt_def(var, askmsg, default)
  set(var) do
	Capistrano::CLI.ui.ask "#{askmsg} [#{default}] : "
  end
  set var, default if eval("#{var.to_s}.empty?")
end

=begin
add a string function to check if a string starts with a particular pattern
=end
def str_start_with (orig_string, little_string)
   return !orig_string.match(/\A#{Regexp.escape(little_string)}/).nil?
end


=begin
uses wget if its a url or use a local 'cp' command if its on a folder 
on the same computer
=end
def get_download_command strUrl
	if (str_start_with(strUrl, "http") or str_start_with(strUrl, "ftp"))
		return "wget " + strUrl 
	else
		return "cp " + strUrl + " ."
	end
end

=begin
Alternative version of get_download_command allows renaming of downloaded 
file to a user specified name
=end
def get_download_command strUrl, strNewName
	if (str_start_with(strUrl, "http") or str_start_with(strUrl, "ftp"))
		return "wget " + strUrl + " -O " + strNewName
	else
		return "cp " + strUrl + " ./"+ strNewName
	end
end


