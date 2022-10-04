# Script for automate the community smell calculation

seed <- 1
set.seed(seed)

#!/usr/bin/env Rscript
library("optparse")

option_list = list(
  make_option(c("-c", "--configuration"), type="character", default=NULL,
              help="Configuration file path", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

# Deve essere specificato il file di configurazione da utilizzare
if (is.null(opt$configuration)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (configuration file).n", call.=FALSE)
}

conf_path = opt$configuration
#conf_path <- "/home/stefano/TesiMagistrale/kaiaulu/conf/helix.yml" #test
print(conf_path)
conf <- yaml::read_yaml(conf_path)

#conf_path <- "../conf/activemq.yml"

require(kaiaulu)
require(stringi)
require(data.table)
require(knitr)
require(visNetwork)

# Yml file for the tools used by kaiaulu
tools_path <- "../tools.yml"

tool <- yaml::read_yaml(tools_path)

# variables from conf e tool yml files
scc_path <- tool[["scc"]]

oslom_dir_path <- tool[["oslom_dir"]]
oslom_undir_path <- tool[["oslom_undir"]]

#conf <- yaml::read_yaml(conf_path)

perceval_path <- tool[["perceval"]]
git_repo_path <- conf[["version_control"]][["log"]]
git_branch <- conf[["version_control"]][["branch"]][1]

start_commit <- conf[["analysis"]][["window"]][["start_commit"]]
end_commit <- conf[["analysis"]][["window"]][["end_commit"]]
window_size <- conf[["analysis"]][["window"]][["size_days"]]

mbox_path <- conf[["mailing_list"]][["mbox"]]
github_replies_path <- conf[["issue_tracker"]][["github"]][["replies"]]
jira_issue_comments_path <- conf[["issue_tracker"]][["jira"]][["issue_comments"]]

project_name <- conf[["issue_tracker"]][["github"]][["repo"]]

start_date <- conf[["analysis"]][["window"]][["start_datetime"]]
end_date <- conf[["analysis"]][["window"]][["end_datetime"]]
start_date <- as.POSIXct(start_date)
end_date <- as.POSIXct(end_date)

# Filters
file_extensions <- conf[["filter"]][["keep_filepaths_ending_with"]]
substring_filepath <- conf[["filter"]][["remove_filepaths_containing"]]



# Function added  STEFANO RONDINELLA
# Function for parse jira file from our database
parse_jira_from_percevaleJson <- function(json_path) {
  require(data.table)

  #json_path= "/home/stefano/TesiMagistrale/kaiaulu/rawdata/issue_tracker/jsonPercevale.json"
  #json_path = "/home/stefano/TesiMagistrale/kaiaulu/rawdata/issue_tracker/activemq_issues-merged.json"

  # Comments list parser. Comments may occur on any json issue.
  jira_parse_comment <- function(comment) {
    parsed_comment <- list()
    parsed_comment[["comment_id"]] <- comment[["id"]]

    parsed_comment[["comment_created_datetimetz"]] <-
      comment[["created"]]
    parsed_comment[["comment_updated_datetimetz"]] <-
      comment[["updated"]]

    parsed_comment[["comment_author_id"]] <-
      comment[["author"]][["name"]]
    parsed_comment[["comment_author_name"]] <-
      comment[["author"]][["displayName"]]
    parsed_comment[["comment_author_timezone"]] <-
      comment[["author"]][["timeZone"]]

    parsed_comment[["comment_author_update_id"]] <-
      comment[["updateAuthor"]][["name"]]
    parsed_comment[["comment_author_update_name"]] <-
      comment[["updateAuthor"]][["displayName"]]
    parsed_comment[["comment_author_update_timezone"]] <-
      comment[["updateAuthor"]][["timeZone"]]

    parsed_comment[["comment_body"]] <- comment[["body"]]

    return(parsed_comment)
  }


  #parse_jira_issue_percevale <- function(json_path){
  #produce una lista
  json_issue_comments <- jsonlite::read_json(json_path)

  # one list contains all issues, the other contains all comments
  all_issues <- list()
  all_issues_comments <- list()

  # list of all objects from json
  json_issue_comments <- jsonlite::read_json(json_path)

  json_issue_comments

  # numbers of issues
  n_issues <- length(json_issue_comments)


  # extract data from all the object and insert in the dataframes
  for (i in 1:n_issues) {
    issue_key <-
      json_issue_comments[[i]][["search_fields"]][["issue_key"]]

    #issue_info <- json_issue_comments[[i]][["comments_data"]]

    # Parse all relevant *issue* fields
    all_issues[[i]] <- data.table(
      issue_key = issue_key,

      issue_summary = json_issue_comments[[i]][["data"]][["fields"]][["summary"]],
      issue_type = json_issue_comments[[i]][["data"]][["fields"]][["issuetype"]][["name"]],
      issue_status = json_issue_comments[[i]][["data"]][["fields"]][["status"]][["name"]],
      issue_resolution = json_issue_comments[[i]][["data"]][["fields"]][["resolution"]][["name"]],
      issue_components = unlist(sapply(
        json_issue_comments[[i]][["data"]][["fields"]][["components"]], "[[", "name"
      )),
      issue_description = json_issue_comments[[i]][["data"]][["fields"]][["description"]],

      issue_created_datetimetz = json_issue_comments[[i]][["data"]][["fields"]][["created"]],
      issue_updated_datetimetz = json_issue_comments[[i]][["data"]][["fields"]][["updated"]],
      issue_resolution_datetimetz = json_issue_comments[[i]][["data"]][["fields"]][["resolutiondate"]],

      issue_creator_id = json_issue_comments[[i]][["data"]][["fields"]][["creator"]][["name"]],
      issue_creator_name = json_issue_comments[[i]][["data"]][["fields"]][["creator"]][["displayName"]],
      issue_creator_timezone = json_issue_comments[[i]][["data"]][["fields"]][["creator"]][["timeZone"]],

      issue_assignee_id = json_issue_comments[[i]][["data"]][["fields"]][["assignee"]][["name"]][[1]],
      issue_assignee_name = json_issue_comments[[i]][["data"]][["fields"]][["assignee"]][["displayName"]][[1]],
      issue_assignee_timezone = json_issue_comments[[i]][["data"]][["fields"]][["assignee"]][["timeZone"]][[1]],

      issue_reporter_id = json_issue_comments[[i]][["data"]][["fields"]][["reporter"]][["name"]],
      issue_reporter_name = json_issue_comments[[i]][["data"]][["fields"]][["reporter"]][["displayName"]],
      issue_reporter_timezone = json_issue_comments[[i]][["data"]][["fields"]][["reporter"]][["timeZone"]]

    )

    # Comments data
    comments_list <-
      json_issue_comments[[i]][["data"]][["comments_data"]]

    # Check if there are comments
    if (length(comments_list) > 0) {
      # Parse all comments into issue_comments
      issue_comments <- rbindlist(lapply(comments_list,
                                         jira_parse_comment))
      # Add issue_key column to the start of the table
      issue_comments <-
        cbind(data.table(issue_key = issue_key), issue_comments)
      all_issues_comments[[i]] <- issue_comments
    }
  }


  all_issues <- rbindlist(all_issues,fill=TRUE)
  all_issues_comments <- rbindlist(all_issues_comments,fill=TRUE)

  parsed_issues_comments <- list()
  parsed_issues_comments[["issues"]] <- all_issues
  parsed_issues_comments[["comments"]] <- all_issues_comments

  project_jira_issues <- parsed_issues_comments[["issues"]]
  project_jira_issues <- project_jira_issues[,.(reply_id=issue_key,
                                                in_reply_to_id=NA_character_,
                                                reply_datetimetz=issue_created_datetimetz,
                                                reply_from=issue_creator_name,
                                                reply_to=NA_character_,
                                                reply_cc=NA_character_,
                                                reply_subject=issue_key,
                                                reply_body=issue_description)]


  project_jira_comments <- parsed_issues_comments[["comments"]]
  project_jira_comments <- project_jira_comments[,.(reply_id=comment_id,
                                                    in_reply_to_id=NA_character_,
                                                    reply_datetimetz=comment_created_datetimetz,
                                                    reply_from=comment_author_name,
                                                    reply_to=NA_character_,
                                                    reply_cc=NA_character_,
                                                    reply_subject=issue_key,
                                                    reply_body=comment_body)]

  project_jira <- rbind(project_jira_issues,
                        project_jira_comments)


  rm(project_jira_issues)
  rm(project_jira_comments)
  rm(parsed_issues_comments)
  rm(all_issues_comments)
  rm(all_issues)
  rm(issue_comments)
  rm(json_issue_comments)


  return(project_jira)

}


print("Unzip jira ...")

#Zipped jira json
jira_zip_path <- paste(jira_issue_comments_path,'.gz',sep='')

# UnZip the jira json file with gzip
gzip_output <- system2('gzip',
                    args = c('-d','-k',jira_zip_path),
                    stdout = TRUE,
                    stderr = FALSE)



# Parse gitlog, they are used for create the collaboration graph
print("Parse gitlog ...")

git_checkout(git_branch,git_repo_path)
project_git <- parse_gitlog(perceval_path,git_repo_path)
project_git <- project_git  %>%
  filter_by_file_extension(file_extensions,"file_pathname")  %>%
  filter_by_filepath_substring(substring_filepath,"file_pathname")



# Parse Replies
print("Parse replies ...")

# BUG USING as.POSIXct
# SOLUTION: using strptime after change local timezone. From : https://stackoverflow.com/questions/13726894/strptime-as-posixct-and-as-date-return-unexpected-na
Sys.setlocale("LC_TIME", "en_GB.UTF-8")

project_git$author_tz <- sapply(stringi::stri_split(project_git$author_datetimetz, regex=" "),"[[",6)

project_git$author_datetimetz <- as.POSIXct(project_git$author_datetimetz,
                                            format = "%a %b %d %H:%M:%S %Y %z", tz = "UTC")


project_git$committer_tz <- sapply(stringi::stri_split(project_git$committer_datetimetz, regex=" "),"[[",6)
project_git$committer_datetimetz <- as.POSIXct(project_git$committer_datetimetz,
                                               format = "%a %b %d %H:%M:%S %Y %z", tz = "UTC")


# Parse mbox
print("Parse mbox ...")

#FIXED PARSE MBOX FUNCTION
parse_mbox2 <- function(perceval_path,mbox_path){
  # Expand paths (e.g. "~/Desktop" => "/Users/someuser/Desktop")
  perceval_path <- path.expand(perceval_path)
  mbox_path <- path.expand(mbox_path)
  # Remove ".mbox"
  mbox_uri <- stri_replace_last(mbox_path,replacement="",regex=".mbox")
  # Use percerval to parse mbox_path. --json line is required to be parsed by jsonlite::fromJSON.
  perceval_output <- system2(perceval_path,
                             args = c('mbox',mbox_uri,mbox_path,'--json-line'),
                             stdout = TRUE,
                             stderr = FALSE)
  # Parsed JSON output as a data.table.
  perceval_parsed <- data.table(jsonlite::stream_in(textConnection(perceval_output),verbose=FALSE))

  if("data.body.plain" %in% colnames(perceval_parsed)){
    data.table::setnames(perceval_parsed,
                         "data.body.plain",
                         "reply_body")
  }else{
    data.table::setnames(perceval_parsed,
                         "data.body",
                         "reply_body")
  }

  # fixed with skip_absent=TRUE, STEFANO RONDINELLA
  data.table::setnames(perceval_parsed,
                       c("data.Date","data.To","data.From","data.Subject","data.Cc","data.Message.ID","data.In.Reply.To"),
                       c("reply_datetimetz","reply_to","reply_from","reply_subject","reply_cc","reply_id","in_reply_to_id"),skip_absent=TRUE)

  perceval_parsed <- perceval_parsed[,.(reply_id,
                                        in_reply_to_id,
                                        reply_datetimetz,
                                        reply_from,
                                        reply_to,
                                        #reply_cc,
                                        reply_subject,
                                        reply_body)]

  return(perceval_parsed)
}



project_mbox <- NULL
project_jira <- NULL
project_github_replies <- NULL

print("Fix timezone ...")

if(!is.null(mbox_path)){
  #project_mbox <- parse_mbox(perceval_path,mbox_path)
  project_mbox <- parse_mbox2(perceval_path,mbox_path)
  project_mbox$reply_tz <- sapply(stringi::stri_split(project_git$reply_datetimetz,
                                                      regex=" "),"[[",6)

  project_mbox$reply_datetimetz <- as.POSIXct(project_mbox$reply_datetimetz,
                                              format = "%a, %d %b %Y %H:%M:%S %z", tz = "UTC")


}
if(!is.null(jira_issue_comments_path)){
  #project_jira <- parse_jira_replies(parse_jira(jira_issue_comments_path))
  project_jira <- parse_jira_from_percevaleJson(jira_issue_comments_path)
  # Timezone is embedded on separated field. All times shown in UTC.
  project_jira$reply_tz <- "0000"

  project_jira$reply_datetimetz <- as.POSIXct(project_jira$reply_datetimetz,
                                              format = "%Y-%m-%dT%H:%M:%S.000+0000", tz = "UTC")
}
if(!is.null(github_replies_path)){
  project_github_replies <- parse_github_replies(github_replies_path)


  # Timezone is not available on GitHub timestamp, all in UTC
  project_github_replies$reply_tz <- "0000"

  project_github_replies$reply_datetimetz <- as.POSIXct(project_github_replies$reply_datetimetz,
                                                        format = "%Y-%m-%dT%H:%M:%S", tz = "UTC")

}


# All replies are combined into a single reply table.
project_reply <- rbind(project_mbox
                       ,project_jira
                       #,project_github_replies
                       , fill= TRUE)

project_git <- project_git[order(author_datetimetz)]

project_reply <- project_reply[order(reply_datetimetz)]




########### SMELL ######################
print("Process community smells ...")

# Window size that we are considering
window_size <- window_size


#Identity matching
project_log <- list(project_git=project_git,project_reply=project_reply)
project_log <- identity_match(project_log,
                              name_column = c("author_name_email","reply_from"),
                              assign_exact_identity,
                              use_name_only=TRUE,
                              label = "raw_name")

project_git <- project_log[["project_git"]]
project_reply <- project_log[["project_reply"]]


# Define all timestamp in number of days since the very first commit of the repo
# Note here the start_date and end_date are in respect to the git log.

# Transform commit hashes into datetime so window_size can be used
#start_date <- get_date_from_commit_hash(project_git,start_commit)
#end_date <- get_date_from_commit_hash(project_git,end_commit)

start_date <- as.POSIXct(start_date)
end_date <- as.POSIXct(end_date)
datetimes <- project_git$author_datetimetz
reply_datetimes <- project_reply$reply_datetimetz

# Format time window for posixT
window_size_f <- stringi::stri_c(window_size," day")

# Note if end_date is not (and will likely not be) a multiple of window_size,
# then the ending incomplete window is discarded so the metrics are not calculated
# in a smaller interval
time_window <- seq.POSIXt(from=start_date,to=end_date,by=window_size_f)

# Create a list where each element is the social smells calculated for a given commit hash
smells <- list()
size_time_window <- length(time_window)
for(j in 2:size_time_window){

  # Initialize
  commit_interval <- NA
  start_day <- NA
  end_day <- NA
  org_silo <- NA
  missing_links <- NA
  radio_silence <- NA
  primma_donna <- NA
  st_congruence <- NA
  communicability <- NA
  num_tz <- NA
  code_only_devs <- NA
  code_files <- NA
  ml_only_devs <- NA
  ml_threads <- NA
  code_ml_both_devs <- NA

  i <- j - 1

  # If the time window is of size 1, then there has been less than "window_size_f"
  # days from the start date.
  if(length(time_window)  == 1){
    # Below 3 month size
    start_day <- start_date
    end_day <- end_date
  }else{
    start_day <- time_window[i]
    end_day <- time_window[j]
  }


  # Obtain all commits from the gitlog which are within a particular window_size
  project_git_slice <- project_git[(author_datetimetz >= start_day) &
                                     (author_datetimetz < end_day)]

  # Obtain all email posts from the reply which are within a particular window_size
  project_reply_slice <- project_reply[(reply_datetimetz >= start_day) &
                                         (reply_datetimetz < end_day)]

  # Check if slices contain data
  gitlog_exist <- (nrow(project_git_slice) != 0)
  ml_exist <- (nrow(project_reply_slice) != 0)


  # Create Networks
  if(gitlog_exist){
    i_commit_hash <- data.table::first(project_git_slice[author_datetimetz == min(project_git_slice$author_datetimetz,na.rm=TRUE)])$commit_hash

    j_commit_hash <- data.table::first(project_git_slice[author_datetimetz == max(project_git_slice$author_datetimetz,na.rm=TRUE)])$commit_hash

    # Parse networks edgelist from extracted data
    network_git_slice <- transform_gitlog_to_bipartite_network(project_git_slice,
                                                               mode="author-file")

    # Community Smells functions are defined base of the projection networks of
    # dev-thread => dev-dev, and dev-file => dev-dev. This creates both dev-dev via graph projections

    git_network_authors <- bipartite_graph_projection(network_git_slice,
                                                      is_intermediate_projection = FALSE,
                                                      mode = TRUE)

    code_clusters <- community_oslom(oslom_undir_path,
                                     git_network_authors,
                                     seed=seed,
                                     n_runs = 1000,
                                     is_weighted = TRUE)

  }
  if(ml_exist){

    network_reply_slice <- transform_reply_to_bipartite_network(project_reply_slice)


    reply_network_authors <- bipartite_graph_projection(network_reply_slice,
                                                        is_intermediate_projection = FALSE,
                                                        mode = TRUE)

    # Community Detection

    mail_clusters <- community_oslom(oslom_undir_path,
                                     reply_network_authors,
                                     seed=seed,
                                     n_runs = 1000,
                                     is_weighted = TRUE)

  }
  # Metrics #

  if(gitlog_exist){
    commit_interval <- stri_c(i_commit_hash,"-",j_commit_hash)
    # Social Network Metrics
    code_only_devs <- length(unique(project_git_slice$identity_id))
    code_files <- length(unique(project_git_slice$file_pathname))

  }
  if(ml_exist){
    # Smell

    radio_silence <- length(smell_radio_silence(mail.graph=reply_network_authors,
                                                clusters=mail_clusters))

    # Social Technical Metrics
    ml_only_devs <- length(unique(project_reply_slice$identity_id))
    ml_threads <- length(unique(project_reply_slice$reply_subject))
  }
  if (ml_exist & gitlog_exist){
    # Smells
    org_silo <- length(smell_organizational_silo(mail.graph=reply_network_authors,
                                                 code.graph=git_network_authors))

    missing_links <- length(smell_missing_links(mail.graph=reply_network_authors,
                                                code.graph=git_network_authors))
    # Social Technical Metrics
    st_congruence <- smell_sociotechnical_congruence(mail.graph=reply_network_authors,
                                                     code.graph=git_network_authors)
    #    communicability <- community_metric_mean_communicability(reply_network_authors,git_network_authors)
    num_tz <- length(unique(c(project_git_slice$author_tz,
                              project_git_slice$committer_tz,
                              project_reply_slice$reply_tz)))
    code_ml_both_devs <- length(intersect(unique(project_git_slice$identity_id),
                                          unique(project_reply_slice$identity_id)))

  }

  # Aggregate Metrics
  smells[[stringi::stri_c(start_day,"|",end_day)]] <- data.table(commit_interval,
                                                                 start_datetime = start_day,
                                                                 end_datetime = end_day,
                                                                 org_silo,
                                                                 missing_links,
                                                                 radio_silence,
                                                                 #primma_donna,
                                                                 st_congruence,
                                                                 #communicability,
                                                                 num_tz,
                                                                 code_only_devs,
                                                                 code_files,
                                                                 ml_only_devs,
                                                                 ml_threads,
                                                                 code_ml_both_devs)
}
smells_interval <- rbindlist(smells)

# Save the Smells dataframe in a csv
file_name <- paste("../rawdata/smell_data/",project_name,"_community_smells.csv", sep="")
write.csv(smells_interval,file_name, row.names = FALSE)

print("End, save the results !")





############ GRAPHS #####################

print("Creating graphs ... ")

project_collaboration_network <- recolor_network_by_community(git_network_authors,code_clusters)

gcid <- igraph::graph_from_data_frame(d=project_collaboration_network[["edgelist"]],
                                      directed = FALSE,
                                      vertices = project_collaboration_network[["nodes"]])

visIgraph(gcid,randomSeed = 1)

# Save the graph
#write_graph(gcid, "../rawdata/project_collaboration_network.txt")

# Save the graph as html
library(visNetwork)
library(htmlwidgets)
graphfile <- paste("../rawdata/graph/",project_name,"_collaboration_network_code_cluster.html", sep = "")
saveWidget(visIgraph(gcid,randomSeed = 1), file = graphfile)


project_collaboration_network <- recolor_network_by_community(reply_network_authors,mail_clusters)

gcid <- igraph::graph_from_data_frame(d=project_collaboration_network[["edgelist"]],
                                      directed = FALSE,
                                      vertices = project_collaboration_network[["nodes"]])

visIgraph(gcid,randomSeed = 1)

# Save the graph as html
library(visNetwork)
library(htmlwidgets)
graphfile <- paste("../rawdata/graph/",project_name,"_collaboration_network_mail_cluster.html", sep = "")
saveWidget(visIgraph(gcid,randomSeed = 1), file = graphfile)

print("Graphs saved !")


print("Delete unzip jira .... ")

# Delete the jira json file
delete_output <- system2('rm',
                    args = c(jira_issue_comments_path),
                    stdout = TRUE,
                    stderr = FALSE)
print()
print()
print()
print(" END !!!")